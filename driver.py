#! /usr/bin/env python3.6
import platform
import sys
import shared.runTest as test
import os
import shutil

def main(*args):
    # input example: 2.0.1-beta.25
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
        # TODO import chocolatey.buildNUPKG as dist
        pass
    else:
        print(f"does not support platform {platformSystem} yet...")
        return

    # at root
    buildFolderName = "build"
    # create folder structure in "output/"
    if os.path.exists(buildFolderName):
        # clear stale data
        print(f"trying to clear build/ directory...")
        shutil.rmtree(buildFolderName)
    os.mkdir(buildFolderName)

    binaryPath = dist.preparePackage(version,buildFolderName)

    assert(test.runExecutable(binaryPath, version))

    artifactFolderName = "artifact"
    if not os.path.exists(artifactFolderName):
        os.mkdir(artifactFolderName)
    # from buildFolder to artifactFolder
    dist.publishArtifact(buildFolderName, artifactFolderName, version)
    
if __name__ == "__main__":
    main(*sys.argv)