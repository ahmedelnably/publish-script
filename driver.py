#! /usr/bin/env python3.6
import platform
import sys
import shared.runTest as test
import os
import shutil
from shared import constants

# 1. build package
# { 2. clean install
#   3. test executable
#   4. uninstall }  => all part of testing


def main(*args):
    # assume follow semantic versioning 2.0.0
    constants.VERSION = args[1]
    platformSystem = platform.system()
    if platformSystem == "Linux":
        d, _, __ = platform.linux_distribution()
        if d == "Ubuntu":
            import ubuntu.bulidDEB as dist
            print("detect Ubuntu, start working on deb package...")
        else:
            print(f"does not support distribution {d} yet...")
            return
    elif platformSystem == "Windows":
        import chocolatey.buildNUPKG as dist
        print("detect Windows, start working on nupkg pacakge...")
    else:
        print(f"does not support platform {platformSystem} yet...")
        return

    # at root
    initWorkingDir(constants.BUILDFOLDER, True)
    initWorkingDir(constants.ARTIFACTFOLDER)

    # 1. build package
    dist.preparePackage()

    def verifyPackage():
        initWorkingDir(constants.TESTFOLDER, True)
        # 2. clean install
        # TODO usually require sudo or administrator privilege
        dist.installPackage()
        # 3. test executable
        assert(test.runExecutable())
        # 4. uninstall
        dist.uninstallPackage()
    # verifyPackage()


def initWorkingDir(dirName, clean = False):
    if clean:
        if os.path.exists(dirName):
            print(f"trying to clear {dirName}/ directory ...")
            shutil.rmtree(dirName)
    print(f"trying to create {dirName}/ directory")
    os.makedirs(dirName, exist_ok=True)

if __name__ == "__main__":
    # input example: 2.0.1-beta.25
    main(*sys.argv)
