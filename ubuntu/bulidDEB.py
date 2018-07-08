#! /usr/bin/env python3.6

# takes in a zip url
# output a deb package
# depends on gzip, dpkg-deb, strip and md5sum

import sys
import os
import wget
import zipfile
import shutil
import subprocess
import datetime
from string import Template
from shared.constants import PACKAGENAME
from shared.helper import restoreDirectory

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

@restoreDirectory
def preparePackage(buildFolder, artiFactFolder, version):
    # for ubuntu, its x64 version only
    fileName = f"Azure.Functions.Cli.linux-x64.{version}.zip"
    url = f'https://functionscdn.azureedge.net/public/{version}/{fileName}'

    debianVersion = returnDebVersion(version)

    # download the zip
    # output to local folder
    if not os.path.exists(fileName):
        print(f"downloading from {url}...")
        wget.download(url)

    # all directories path are relative
    packageFolder = f"{PACKAGENAME}_{debianVersion}"
    root = os.path.join(buildFolder, packageFolder)
    usr = os.path.join(root, "usr")
    usrlib = os.path.join(usr, "lib")
    usrlibFunc = os.path.join(usrlib, PACKAGENAME)
    os.makedirs(usrlibFunc)
    # unzip here
    with zipfile.ZipFile(fileName) as f:
        print(f"extracting to {usrlibFunc}...")
        f.extractall(usrlibFunc)

    # create relative symbolic link under bin directory, change mode to executable
    usrbin = os.path.join(usr, "bin")
    os.makedirs(usrbin)
    # cd into usr/bin, create relative symlink
    os.chdir(usrbin)
    print("trying to create symlink for func...")
    os.symlink(f"../lib/{PACKAGENAME}/func", "func")
    # executable to be returned
    exeFullPath = os.path.abspath("func")

    # go back to root
    os.chdir("../..")
    # strip sharedobjects
    subprocess.run(
        "find -name *.so | xargs strip --strip-unneeded", shell=True)

    document = os.path.join("usr", "share", "doc", PACKAGENAME)
    os.makedirs(document)
    # write copywrite
    print("include MIT copyright")
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    shutil.copyfile(os.path.join(scriptDir, "copyright"),
                    os.path.join(document, "copyright"))
    # write changelog
    with open(os.path.join(scriptDir, "changelog_template")) as f:
        stringData = f.read()  # read until EOF
    t = Template(stringData)
    # datetime example: Tue, 06 April 2018 16:32:31
    time = datetime.datetime.utcnow().strftime("%a, %d %b %Y %X")
    with open(os.path.join(document, "changelog.Debian"), "w") as f:
        print(f"writing changelog with date utc: {t}")
        f.write(t.safe_substitute(DEBIANVERSION=debianVersion, DATETIME=time, VERSION=version, PACKAGENAME=PACKAGENAME))
    # by default gzip compress file 'in place
    subprocess.run(
        ["gzip", "-9", "-n", os.path.join(document, "changelog.Debian")])

    debian = "DEBIAN"
    os.makedirs(debian)
    # get all files under usr/ and produce a md5 hash
    print("trying to produce md5 hashes...")
    subprocess.run(
        "find usr/* -type f | xargs md5sum > DEBIAN/md5sums", shell=True)

    # produce the control file from template
    with open(os.path.join(scriptDir, "control_template")) as f:
        stringData = f.read()
    t = Template(stringData)
    with open(os.path.join(debian, "control"), "w") as f:
        print("trying to write control file...")
        f.write(t.safe_substitute(DEBIANVERSION=debianVersion, PACKAGENAME=PACKAGENAME))

    # before publish
    print(f"change permission of files in {os.getcwd()}")
    for r, ds, fs in os.walk(os.getcwd()):
        for d in ds:
            # folder permission to 755
            os.chmod(os.path.join(r, d), 0o755)
        for f in fs:
            # file permission to 644
            os.chmod(os.path.join(r, f), 0o644)
    print(f"change bin/func permission to 755")
    # octal
    os.chmod(exeFullPath, 0o755)

    os.chdir("../..") 
    print("trying to produce deb file...")
    subprocess.run(["fakeroot", "dpkg-deb", "--build",
                   os.path.join(buildFolder, packageFolder), os.path.join(artiFactFolder, packageFolder+".deb")])
