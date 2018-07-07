#! /usr/bin/env python3.6
import os
import sys

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