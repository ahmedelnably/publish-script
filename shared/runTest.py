#! /usr/bin/env python3.6
import sys
import os
import shutil
import time
import signal
from .helper import restoreDirectory
from .helper import printReturnOutput
from . import constants

@restoreDirectory
def runExecutable():
    # 1. check the version output
    # TODO print output as well as test for version
    output = printReturnOutput([constants.CMD])
    assert(f"Azure Functions Core Tools ({constants.VERSION})" in output)
    # make sure command used in this test scripts are presented in the help
    assert("init " in output)
    assert("new " in output)
    assert("start " in output)

    # 2. test ability to create function
    os.chdir(constants.TESTFOLDER)

    # 2.1 func init
    # FIXME ...why is the output contains dotnet new?
    output = printReturnOutput(
        [constants.CMD, "init", "--worker-runtime", 'dotnet'])
    assert("was created successfully" in output)
    assert(os.path.exists("host.json"))
    assert(os.path.exists("test.csproj"))

    # 2.2 func new
    functionName = "dummyHttp"
    # test csx since its scripting language, does not require additional runtimes
    output = printReturnOutput(
        [constants.CMD, "new", "--csx", "-t", "Http Trigger", "-n", functionName])
    assert(os.path.exists(os.path.join(functionName,"run.csx")))
    # TODO 2.3 func start
    # actually invoke dotnet core, which may test some dependencies for installation

    return True
