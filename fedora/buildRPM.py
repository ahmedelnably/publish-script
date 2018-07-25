#! /usr/bin/env python3.6
import os
import wget
import zipfile
import datetime
import shutil
from string import Template
from shared import constants
from shared.helper import restoreDirectory
from shared.helper import produceHashForfile
from shared.helper import printReturnOutput

DEPENDENCY = "dotnet-runtime-deps-2.1"
DEPENDENCYVERSION = ">= 2.1.1"

def returnRpmVersion(version):
    # http://ftp.rpm.org/max-rpm/s1-rpm-inside-tags.html
    # The version tag defines the version of the software being packaged. 
    # The version specified should be as close as possible to the format of the original software's version. 
    # In most cases, there should be no problem specifying the version just as the software's original developer did. 
    # However, there is a restriction. There can be no dashes in the version. If you forget, RPM will remind you: 
    strlist = version.split('-')
    if len(strlist) == 1:
        return strlist[0]
    elif len(strlist) == 2:
        return f"{strlist[0]}~{strlist[1]}"
    else:
        raise NotImplementedError

# output a rpm package
# depends on rpmdevtools, strip, tar
@restoreDirectory
def preparePackage():
    # for linux, its x64 version only (ubuntu has already dropped x86 support)
    fileName = f"Azure.Functions.Cli.linux-x64.{constants.VERSION}.zip"
    url = f'https://functionscdn.azureedge.net/public/{constants.VERSION}/{fileName}'

    # download the zip
    # output to local folder
    if not os.path.exists(fileName):
        print(f"downloading from {url}")
        wget.download(url)

    rpmVersion = returnRpmVersion(constants.VERSION)
    # massage files then put them into ~/rpmbuild/SOURCES
    # TODO copy from deb, make this true for all linux
    # all directories path are relative
    packageFolder = f"{constants.PACKAGENAME}-{rpmVersion}"
    root = os.path.join(constants.BUILDFOLDER, packageFolder)
    usr = os.path.join(root, "usr")
    usrlib = os.path.join(usr, "lib")
    usrlibFunc = os.path.join(usrlib, constants.PACKAGENAME)
    os.makedirs(usrlibFunc)
    # unzip here
    with zipfile.ZipFile(fileName) as f:
        print(f"extracting to {usrlibFunc}")
        f.extractall(usrlibFunc)

    # create relative symbolic link under bin directory, change mode to executable
    usrbin = os.path.join(usr, "bin")
    os.makedirs(usrbin)
    # cd into usr/bin, create relative symlink
    os.chdir(usrbin)
    print("create symlink for func")
    os.symlink(f"../lib/{constants.PACKAGENAME}/func", "func")
    exeFullPath = os.path.abspath("func")

    # go back to root
    os.chdir("../..")
    # strip sharedobjects
    # TODO use glob module
    printReturnOutput(["find", "-name", "*.so", "|", "xargs", "strip", "--strip-unneeded"], shell=True)

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

    # setting up rpm packaging work space at ~/rpmbuild
    printReturnOutput(["rpmdev-setuptree"])
    RpmBuildAbs = os.path.join(os.environ['HOME'], "rpmbuild")

    # tar the build/ and put it in rpmbuild/SOURCE
    printReturnOutput(["tar", "-czvf", os.path.join(RpmBuildAbs, "SOURCES", f"{packageFolder}.tar.gz"), "../"])

    print("produce .spec under ~/rpmbuild/SPECS/")
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(scriptDir, "spec_template")) as f:
        stringData = f.read()
    t = Template(stringData)
    # TODO fix date sub
    time = datetime.datetime.utcnow().strftime("%a %b %d %Y")
    with open(os.path.join(RpmBuildAbs, "SPECS", f"{constants.PACKAGENAME}.spec"), 'w') as f:
        f.write(t.safe_substitute(PACKAGENAME=constants.PACKAGENAME, RPMVERSION=rpmVersion, DEPENDENCY=DEPENDENCY, DEPENDENCYVERSION=DEPENDENCYVERSION, DATE=time))
    
    os.chdir(os.path.join(RpmBuildAbs,"SPECS"))
    output = printReturnOutput(["rpmbuild", "-bb", f"{constants.PACKAGENAME}.spec"])

    # get package name from output
    # Wrote: /home/shun/rpmbuild/RPMS/x86_64/azure-functions-core-tools-2.0.1~beta.33-1.fc27.x86_64.rpm
    suffix = ".rpm"
    prefix = "RPMS/x86_64"
    end = output.find(suffix)+len(suffix)
    start = output.rfind(prefix,0,end) + len(prefix)+1
    rpmName = output[start:end]

    # ~/rpmbuild/RPMS is where we find output RPMS, we are going to copy it to constants.ARTIFACT
    print(f"copy result to {os.path.join(constants.ARTIFACTFOLDER, rpmName)}")
    shutil.copyfile(os.path.join(RpmBuildAbs, prefix, rpmName), os.path.join(constants.DRIVERROOTDIR, constants.ARTIFACTFOLDER, rpmName))
