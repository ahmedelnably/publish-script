#! /usr/bin/env python3.6
import subprocess
import sys
import os
import shutil
import time
import signal
from .helper import restoreDirectory
from .constants import CMD

@restoreDirectory
def runExecutable(testFolder, version):
    print("performing basic functionality test on func...")
    # 1. check the version output
    # TODO print output as well as test for version
    print("verify func...")
    stdout = subprocess.check_output(CMD).decode('ascii')
    versionOutput = f"Azure Functions Core Tools ({version})"
    assert(versionOutput in stdout)
    # make sure command used in this test scripts are presented in the help
    assert("init " in stdout)
    assert("new " in stdout)
    assert("start " in stdout)

    # 2. test ability to create function
    os.chdir(testFolder)

    # 2.1 func init
    print("verfiy func init...")
    stdout = subprocess.check_output(
        [CMD, "init", "--worker-runtime", "dotnet"]).decode('ascii')
    assert("was created successfully" in stdout)
    assert(os.path.exists("host.json"))
    assert(os.path.exists("test.csproj"))
    # 2.2 func new
    functionName = "dummyHttp"
    print("verify func new...")
    stdout = subprocess.check_output(
        [CMD, "new", "-l", "C#", "-t", "HttpTrigger", "-n", functionName]).decode('ascii')
    assert("was created successfully" in stdout)
    assert(os.path.exists(f"{functionName}.cs"))
    # 2.3 func start
    # print("verify func start...")
    # popen = subprocess.Popen([CMD, "start", "--build"],
    #                          stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
    # # FIXME
    # # wait a bit, then send control-c as suggested
    # time.sleep(10)
    # popen.send_signal(signal.SIGINT)
    # stdout = popen.stdout.read()
    # assert(f"{testFolder}.{functionName}.Run" in stdout)
    # assert("Generating 1 job function(s)" in stdout)
    # assert(f"{functionName}: http://localhost:7071/api/{functionName}" in stdout)

    return True


if __name__ == "__main__":
    runExecutable(sys.argv[1], sys.argv[2])
