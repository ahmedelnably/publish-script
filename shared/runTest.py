#! /usr/bin/env python3.6
import subprocess
import sys
import os
import shutil
import time
import signal

def runExecutable(pathToExecutable, version):
    print("performing basic functionality test on func...")
    stackD = []
    # 1. check the version output
    # simply call run(), stdout is side effect of the function
    absolutePath = os.path.join(os.getcwd(),pathToExecutable)
    # TODO print output as well as test for version
    print("verify func...")
    stdout = str(subprocess.check_output(absolutePath))
    versionOutput = f"Azure Functions Core Tools ({version})"
    assert(versionOutput in stdout)
    # make sure command used in this test scripts are presented in the help
    assert("init " in stdout)
    assert("new " in stdout)
    assert("start " in stdout)

    # 2. test ability to create function
    testFolder = "test"
    if os.path.exists(testFolder):
        shutil.rmtree(testFolder)
    os.makedirs(testFolder)

    # TODO write a helper function to enclose this in USING
    stackD.append(os.getcwd())
    os.chdir(testFolder)

    # 2.1 func init
    print("verfiy func init...")
    stdout = str(subprocess.check_output([absolutePath, "init", "--worker-runtime", "dotnet"]))
    assert("was created successfully" in stdout)
    assert(os.path.exists("host.json"))
    assert(os.path.exists("test.csproj"))
    # 2.2 func new
    functionName = "dummyHttp"
    print("verify func new...")
    stdout = str(subprocess.check_output([absolutePath, "new", "-l", "C#", "-t", "HttpTrigger","-n", functionName]))
    assert("was created successfully" in stdout)
    assert(os.path.exists(f"{functionName}.cs"))
    # 2.3 func start
    print("verify func start...")
    popen = subprocess.Popen([absolutePath, "start", "--build"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
    # FIXME 
    # wait a bit, then send control-c as suggested
    time.sleep(10)
    popen.send_signal(signal.SIGINT)
    stdout = popen.stdout.read()
    assert(f"{testFolder}.{functionName}.Run" in stdout)
    assert("Generating 1 job function(s)" in stdout)
    assert(f"{functionName}: http://localhost:7071/api/{functionName}" in stdout)
    
    previousDir = stackD.pop()
    os.chdir(previousDir)
    return True
    
if __name__ == "__main__":
    runExecutable(sys.argv[1], sys.argv[2])