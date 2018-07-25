#! /usr/bin/env python3.6
import os
import wget
import zipfile
import datetime
import shutil
from string import Template
from shared import constants
from shared import helper

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
@helper.restoreDirectory
def preparePackage():
    os.chdir(constants.DRIVERROOTDIR)

    rpmVersion = returnRpmVersion(constants.VERSION)
    packageFolder = f"{constants.PACKAGENAME}-{rpmVersion}"
    buildFolder = os.path.join(os.getcwd(), constants.BUILDFOLDER, packageFolder)
    helper.linuxOutput(buildFolder)

    # massage files then put them into ~/rpmbuild/SOURCES
    # setting up rpm packaging work space at ~/rpmbuild
    helper.printReturnOutput(["rpmdev-setuptree"])
    RpmBuildAbs = os.path.join(os.environ['HOME'], "rpmbuild")

    os.chdir(buildFolder)
    # tar the build/ and put it in rpmbuild/SOURCE
    helper.printReturnOutput(["tar", "-czvf", os.path.join(RpmBuildAbs, "SOURCES", f"{packageFolder}.tar.gz"), "../"])

    print("produce .spec under ~/rpmbuild/SPECS/")
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(scriptDir, "spec_template")) as f:
        stringData = f.read()
    t = Template(stringData)
    time = datetime.datetime.utcnow().strftime("%a %b %d %Y")
    deps = []
    for key, value in constants.LINUXDEPS.items():
        entry = f"{key} {value}"
        deps.append(entry)
    deps = ",".join(deps)
    with open(os.path.join(RpmBuildAbs, "SPECS", f"{constants.PACKAGENAME}.spec"), 'w') as f:
        f.write(t.safe_substitute(PACKAGENAME=constants.PACKAGENAME, RPMVERSION=rpmVersion, DEPENDENCY=deps, DATE=time))
    
    os.chdir(os.path.join(RpmBuildAbs,"SPECS"))
    output = helper.printReturnOutput(["rpmbuild", "-bb", f"{constants.PACKAGENAME}.spec"])

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