#! /usr/bin/env python3.6
import os
import sys
import hashlib
import subprocess

def restoreDirectory(f):
    def inner(*args, **kwargs):
        currentDir = os.getcwd()
        returnV = f(*args, **kwargs)
        os.chdir(currentDir)
        return returnV
    return inner

# for some commands, returnCode means success
# for others you need to verify the output string yourself
def printReturnOutput(args, shell=False):
    begin = '=' * 38 +  "Running Subprocess" + "=" * 38
    print(begin)
    print(' '.join(args))
    # DEBUG hit any key to continue, for debug purpose
    # input('...Continue? hit "Enter" to Confirm')
    output = '-' * 40 + "Console Output" + "-" * 40
    print(output)
    try:
        binary = subprocess.check_output(args, shell=shell)
        if len(binary) < 1:
            string = None
        else:
            string = binary.decode('ascii')
        print(string)
        footer = "=" * 94
        print(footer)
        return string
    except subprocess.CalledProcessError:
        # rerun the command, direct output to stdout
        subprocess.call(args)
        raise

BUFFERSIZE = 1024
def produceHashForfile(filePath, hashType, Upper = True):
    # hashType is string name iof
    hashobj = hashlib.new(hashType)
    with open(filePath,'rb') as f:
       buf = f.read(BUFFERSIZE)
       while len(buf) > 0:
           hashobj.update(buf)
           buf = f.read(BUFFERSIZE)
    if Upper:
        return hashobj.hexdigest().upper()
    else:
        return hashobj.hexdigest().lower()