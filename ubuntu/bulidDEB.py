#! /usr/bin/env python3.6
import os
import wget
import zipfile
import shutil
import datetime
from string import Template
from shared import constants
from shared.azurekeyvault import get_secret
from shared import helper

publishVersions = {"18.04LTS_bionic": "5a9dc3f2424a5c053cc3ff2e", 
                "17.10_artful":"59d3d49df3c7fa07032ce371", 
                "16.04LTS_xenial": "582bd623ae062a5d0fec5b8c"}

def returnDebVersion(version):
    # version used in url is provided from user input
    # version used for packaging .deb package needs a slight modification
    # for beta, change to tilde, so it will be placed before rtm versions in apt
    # https://unix.stackexchange.com/questions/230911/what-is-the-meaning-of-the-tilde-in-some-debian-openjdk-package-version-string/230921
    strlist = version.split('-')
    if len(strlist) == 1:
        return strlist[0]+"-1"
    elif len(strlist) == 2:
        return f"{strlist[0]}~{strlist[1]}-1"
    else:
        raise NotImplementedError

# output a deb package
# depends on gzip, dpkg-deb, strip
@helper.restoreDirectory
def preparePackage():
    os.chdir(constants.DRIVERROOTDIR)

    debianVersion = returnDebVersion(constants.VERSION)
    packageFolder = f"{constants.PACKAGENAME}_{debianVersion}"
    buildFolder = os.path.join(os.getcwd(), constants.BUILDFOLDER, packageFolder)
    helper.linuxOutput(buildFolder)

    os.chdir(buildFolder)
    document = os.path.join("usr", "share", "doc", constants.PACKAGENAME)
    os.makedirs(document)
    # write copywrite
    print("include MIT copyright")
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    shutil.copyfile(os.path.join(scriptDir, "copyright"), os.path.join(document, "copyright"))
    # write changelog
    with open(os.path.join(scriptDir, "changelog_template")) as f:
        stringData = f.read()  # read until EOF
    t = Template(stringData)
    # datetime example: Tue, 06 April 2018 16:32:31
    time = datetime.datetime.utcnow().strftime("%a, %d %b %Y %X")
    with open(os.path.join(document, "changelog.Debian"), "w") as f:
        print(f"writing changelog with date utc: {time}")
        f.write(t.safe_substitute(DEBIANVERSION=debianVersion, DATETIME=time, VERSION=constants.VERSION, PACKAGENAME=constants.PACKAGENAME))
    # by default gzip compress file in place
    output = helper.printReturnOutput(["gzip", "-9", "-n", os.path.join(document, "changelog.Debian")])
    helper.chmodFolderAndFiles(os.path.join("usr", "share"))

    debian = "DEBIAN"
    os.makedirs(debian)
    # get all files under usr/ and produce a md5 hash
    print("trying to produce md5 hashes")
    with open('DEBIAN/md5sums', 'w') as md5file:
        # iterate over all files under usr/
        # get their md5sum
        for dirpath, _, filenames in os.walk('usr'):
            for f in filenames:
                filepath = os.path.join(dirpath, f)
                if not os.path.islink(filepath):
                    h = helper.produceHashForfile(filepath, 'md5', Upper=False)
                    md5file.write(f"{h}  {filepath}\n")

    # produce the control file from template
    deps = []
    for key, value in constants.LINUXDEPS.items():
        entry = f"{key} ({value})"
        deps.append(entry)
    deps = ','.join(deps)
    with open(os.path.join(scriptDir, "control_template")) as f:
        stringData = f.read()
    t = Template(stringData)
    with open(os.path.join(debian, "control"), "w") as f:
        print("trying to write control file")
        f.write(t.safe_substitute(DEBIANVERSION=debianVersion, PACKAGENAME=constants.PACKAGENAME, DEPENDENCY=deps))
    helper.chmodFolderAndFiles(debian)

    postinst = ''
    with open(os.path.join(scriptDir, "postinst_template")) as f:
        postinst = f.read()
    with open(os.path.join(debian, "postinst"), "w") as f:
        print("trying to write postinst file")
        f.write(postinst)

    # postinstall has to be 0755 in order for it to work.
    os.chmod(os.path.join(debian, "postinst"), 0o755)

    os.chdir(constants.DRIVERROOTDIR) 
    output = helper.printReturnOutput(["fakeroot", "dpkg-deb", "--build",
                   os.path.join(constants.BUILDFOLDER, packageFolder), os.path.join(constants.ARTIFACTFOLDER, packageFolder+".deb")])
    assert(f"building package '{constants.PACKAGENAME}'" in output)
    

def installPackage():
    debVersion = returnDebVersion(constants.VERSION)
    deb = os.path.join(constants.ARTIFACTFOLDER,f"{constants.PACKAGENAME}_{debVersion}.deb")
    # -f fix broken dependency
    output = helper.printReturnOutput(["sudo", "apt", "install", "-f", "./"+deb, "-y"])
    coreTools = f"Setting up {constants.PACKAGENAME} ({debVersion})" in output
    coreDeps = True
    # if dotnet core sdk is installed, dependency will not be installed again
    # for key in constants.LINUXDEPS.keys():
    #     coreDeps = (f"Setting up {key}" in output) and coreDeps
    deja = f"{constants.PACKAGENAME} is already the newest version ({debVersion})" in output
    assert((coreTools and coreDeps) or deja)

def uninstallPackage():
    debVersion = returnDebVersion(constants.VERSION)
    output = helper.printReturnOutput(["sudo", "dpkg", "--remove", constants.PACKAGENAME])
    assert(f"Removing {constants.PACKAGENAME} ({debVersion})" in output)
    output = helper.printReturnOutput(["sudo", "apt-get", "autoremove", "-y"])
    # if user has dotnet core installed, this dependency can not be removed
    # assert(f"Removing {DEPENDENCY}" in output)

def publish():
    for key, value in publishVersions.items():
        if not helper.getUserConfirm(f"publish for {key}"):
            continue
        config = os.path.join(constants.ARTIFACTFOLDER,key)
        if not os.path.exists(config):
            print("can not find publish config. create new")
            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),"config_template")) as f:
                stringData = f.read()
            t = Template(stringData)
            # retrieve password from keyvault
            pw = get_secret("functionlinuxpublish")
            print("trying to construct a config file")
            with open(config,"w") as f:
                f.write(t.safe_substitute(PW=pw, REPO=value))
        helper.printReturnOutput(["repoapi_client", "-config", os.path.join(constants.ARTIFACTFOLDER,key),
         "-addfile", os.path.join(constants.ARTIFACTFOLDER,f"{constants.PACKAGENAME}_{returnDebVersion(constants.VERSION)}.deb")], confirm=True)