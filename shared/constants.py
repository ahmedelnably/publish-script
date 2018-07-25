#! /usr/bin/env python3.6

# same for all different OSes
PACKAGENAME = "azure-functions-core-tools"
CMD = "func"
ARTIFACTFOLDER = "artifact"
BUILDFOLDER = "build"
TESTFOLDER = "test"

# to be set in driver.py
# do not use it as default argument!!
VERSION = NotImplementedError
DRIVERROOTDIR = NotImplementedError