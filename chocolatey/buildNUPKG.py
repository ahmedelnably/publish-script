#! /usr/bin/env python3.6

# depends on chocolaty
import os
import wget
import sys
import platform
from string import Template
from shared import constants
from shared.helper import printReturnOutput
from shared.helper import produceHashForfile

HASH = "SHA512"
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
# output a deb nupkg
# depends on chocolatey
def preparePackage():
    # adding support for x64
    osBit = platform.architecture()[0].replace('bit', '')
    fileName = f"Azure.Functions.Cli.win-x{osBit}.{constants.VERSION}.zip"
    url = f'https://functionscdn.azureedge.net/public/{constants.VERSION}/{fileName}'

    # version used in url is provided from user input
    # version used for packaging nuget packages needs a slight modification
    chocoVersion = getChocoVersion(constants.VERSION)
    


    # download the zip
    # output to local folder
    if not os.path.exists(fileName):
        print(f"downloading from {url}")
        wget.download(url)

    # get the checksum
    fileHash = produceHashForfile(fileName, HASH)
    
    tools = os.path.join(constants.BUILDFOLDER, "tools")
    os.makedirs(tools)

    # write install powershell script
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(scriptDir, "installps_template")) as f:
        # TODO stream replace instead of reading the entire string into memory
        stringData = f.read() 
    t = Template(stringData)
    with open(os.path.join(tools, "chocolateyinstall.ps1"), "w") as f:
        print("writing install powershell script")
        f.write(t.safe_substitute(ZIPURL=url, PACKAGENAME=constants.PACKAGENAME, CHECKSUM=fileHash, HASHALG=HASH))

    # write nuspec package metadata
    with open(os.path.join(scriptDir,"nuspec_template")) as f:
        stringData = f.read()
    t = Template(stringData)
    nuspecFile = os.path.join(constants.BUILDFOLDER, constants.PACKAGENAME+".nuspec")
    with open(nuspecFile,'w') as f:
        print("writing nuspec")
        f.write(t.safe_substitute(PACKAGENAME=constants.PACKAGENAME, CHOCOVERSION=chocoVersion))
    
    # run choco pack, stdout is merged into python interpreter stdout
    output = printReturnOutput(["choco", "pack", nuspecFile, "--outputdirectory", constants.ARTIFACTFOLDER])
    assert("Successfully created package" in output)
    
def installPackage():
    chocoVersion = getChocoVersion(constants.VERSION)
    nupkg = os.path.join(constants.ARTIFACTFOLDER, f"{constants.PACKAGENAME}.{chocoVersion}.nupkg")
    output = printReturnOutput(["choco", "install", nupkg, '-y'])
    firstTime = f"{constants.PACKAGENAME} package files install completed" in output
    deja = f"{constants.PACKAGENAME} v{chocoVersion} already installed" in output
    assert(firstTime or deja)
    # TODO verify that under %ChocolateyInstall%/lib has the install script and unzip executable

def uninstallPackage():
    output = printReturnOutput(["choco", "uninstall", constants.PACKAGENAME])
    assert(f"{constants.PACKAGENAME} has been successfully uninstalled" in output)
    
# FIXME why does this line not work when import module from sibling package
if __name__ == "__main__":
    # preparePackage(*sys.argv[1:])
    pass
