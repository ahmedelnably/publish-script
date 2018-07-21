#! /usr/bin/env python3.6
import os
import sys
import hashlib

def restoreDirectory(f):
    def inner(*args, **kwargs):
        currentDir = os.getcwd()
        returnV = f(*args, **kwargs)
        os.chdir(currentDir)
        return returnV
    return inner

# TODO beautify
def printToConsole(binary):
    equals = '='*40
    consoleout = equals+"Console Ouput"+equals
    print(consoleout)
    sys.stdout.buffer.write(binary)
    print(consoleout)

BUFFERSIZE = 1024
def produceHashForfile(filePath, hashType):
    # hashType is string name iof
    hashobj = hashlib.new(hashType)
    with open(filePath,'rb') as f:
       buf = f.read(BUFFERSIZE)
       while len(buf) > 0:
           hashobj.update(buf)
           buf = f.read(BUFFERSIZE)
    return hashobj.hexdigest().upper()