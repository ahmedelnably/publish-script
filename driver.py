#! /usr/bin/env python3.6
import platform
import sys
import shared.runTest as test
import os
import shutil

artifactFolderName = "artifact"
buildFolderName = "build"
testFolderName = "test"

# 1. build package
# { 2. clean install
#   3. test executable
#   4. uninstall }  => all part of testing


def main(*args):
    # assume follow semantic versioning 2.0.0
    version = args[1]
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
    # TODO write helper function instead of repetition
    if os.path.exists(buildFolderName):
        # clear stale data
        print(f"trying to clear {buildFolderName}/ directory...")
        shutil.rmtree(buildFolderName)
    os.mkdir(buildFolderName)

    if not os.path.exists(artifactFolderName):
        os.mkdir(artifactFolderName)

    if os.path.exists(testFolderName):
        print(f"trying to clear {testFolderName}/ directory...")
        shutil.rmtree(testFolderName)
    os.makedirs(testFolderName)

    # 1. build package
    dist.preparePackage(buildFolderName, artifactFolderName, version)

    def verifyPackage():
        # 2. clean install
        # TODO usually require sudo or administrator privilege
        dist.installPackage(artifactFolderName, version)
        # 3. test executable
        assert(test.runExecutable(testFolderName, version))
        # 4. uninstall
        dist.uninstallPackage(artifactFolderName, version)
    verifyPackage()


if __name__ == "__main__":
    # input example: 2.0.1-beta.25
    main(*sys.argv)
