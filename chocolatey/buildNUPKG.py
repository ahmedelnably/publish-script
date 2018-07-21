#! /usr/bin/env python3.6
import os
import wget
import sys
import subprocess
from string import Template
from shared import constants
from shared.helper import printToConsole
from shared.helper import produceHashForfile

def getChocoVersion(version):
    # chocolatey do not support semantic versioning2.0.0 yet
    # https://github.com/chocolatey/choco/issues/1610
    # look for hypen, and remove any dots after
    strlist = version.split('-')
    if len(strlist) == 1:
        return strlist[0]
    elif len(strlist) == 2:
        # prerelease
        return f"{strlist[0]}-{strlist[1].replace('.','')}"
    else:
        raise NotImplementedError

# for windows, there's v1 and v2 versions
# assume buildFolder is clean
def preparePackage(version = constants.VERSION):
    # for windows, its x86 version only
    fileName = f"Azure.Functions.Cli.win-x86.{version}.zip"
    url = f'https://functionscdn.azureedge.net/public/{version}/{fileName}'

    # version used in url is provided from user input
    # version used for packaging nuget packages needs a slight modification
    chocoVersion = getChocoVersion(version)

    # download the zip
    # output to local folder
    if not os.path.exists(fileName):
        print(f"downloading from {url}...")
        wget.download(url)

    # get the checksum
    sha512 = produceHashForfile(fileName, 'sha512')
    
    tools = os.path.join(constants.BUILDFOLDER, "tools")
    os.makedirs(tools)

    # write install powershell script
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(scriptDir, "installps_template")) as f:
        # TODO stream replace instead of reading the entire string into memory
        stringData = f.read() 
    t = Template(stringData)
    with open(os.path.join(tools, "chocolateyinstall.ps1"), "w") as f:
        print("writing install powershell script...")
        f.write(t.safe_substitute(ZIPURL=url, PACKAGENAME=constants.PACKAGENAME, CHECKSUM=sha512))

    # write nuspec package metadata
    with open(os.path.join(scriptDir,"nuspec_template")) as f:
        stringData = f.read()
    t = Template(stringData)
    nuspecFile = os.path.join(constants.BUILDFOLDER, constants.PACKAGENAME+".nuspec")
    with open(nuspecFile,'w') as f:
        print("writing nuspec...")
        f.write(t.safe_substitute(PACKAGENAME=constants.PACKAGENAME, CHOCOVERSION=chocoVersion))
    
    print("building package...")
    # run choco pack, stdout is merged into python interpreter stdout
    binary = subprocess.check_output(["choco", "pack", nuspecFile, "--outputdirectory", constants.ARTIFACTFOLDER])
    printToConsole(binary)
    assert("Successfully created package" in binary.decode('ascii'))
    
    
def installPackage(version = constants.VERSION):
    nupkg = os.path.join(constants.ARTIFACTFOLDER, f"{constants.PACKAGENAME}.{getChocoVersion(version)}.nupkg")
    print(f"installing {nupkg}...")
    binary = subprocess.check_output(["choco", "install", nupkg, '-y'])
    printToConsole(binary)
    assert(f"{constants.PACKAGENAME} package files install completed" in binary.decode('ascii'))
    # TODO verify that under %ChocolateyInstall%/lib has the install script and unzip executable

def uninstallPackage(version = constants.VERSION):
    print(f"uninstalling {constants.PACKAGENAME}...")
    binary = subprocess.check_output(["choco", "uninstall", constants.PACKAGENAME])
    printToConsole(binary)
    assert(f"{constants.PACKAGENAME} has been successfully uninstalled" in binary.decode('ascii'))
    
# FIXME why does this line not work when import module from sibling package
if __name__ == "__main__":
    # preparePackage(*sys.argv[1:])
    pass