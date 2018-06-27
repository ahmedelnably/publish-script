#! /usr/bin/env python3

# takes in a zip url
# output a deb package

import sys
import os
import wget
import zipfile
import shutil
import subprocess
import datetime

# input example: 2.0.1-beta.25
version = sys.argv[1]
fileName = f"Azure.Functions.Cli.linux-x64.{version}.zip"
url = f'https://functionscdn.azureedge.net/public/{version}/{fileName}'

# version used in url is provided from user input
# version used for packaging .deb package needs a slight modification
# for beta, change to tilde, so it will be placed before rtm versions in apt
debianVersion = f'{version.replace("-beta", "~beta")}-1'

# download the zip
# output to local folder, using name fileName
if not os.path.exists(fileName):
    print(f"downloading from {url}...")
    wget.download(url)

# create folder structure in "output/"
outputDir = "output"
if os.path.exists(outputDir):
    # clear stale data
    print(f"trying to clear output directory...")
    shutil.rmtree(outputDir)

# output dir is empty
# all directories path are relative
packageName = "azure-functions-core-tools"
root = f"{outputDir}/{packageName}_{debianVersion}"
usr = f"{root}/usr"
usrlib = f"{usr}/lib"
usrlibFunc = f"{usrlib}/{packageName}"
os.makedirs(usrlibFunc)
# unzip here
with zipfile.ZipFile(fileName) as f:
    print(f"extracting to {usrlibFunc}...")
    f.extractall(usrlibFunc)

# create relative symbolic link under bin directory, change mode to executable
usrbin = f"{usr}/bin"
os.makedirs(usrbin)
# cd into usr/bin, create relative symlink
os.chdir(usrbin)
print("trying to create symlink for func...")
os.symlink(f"../lib/{packageName}/func","func")

# go back to root
os.chdir("../..")
# strip sharedobjects
subprocess.run("find -name *.so | xargs strip --strip-unneeded", shell=True)

document = f"usr/share/doc/{packageName}"
os.makedirs(document)
# write copywrite
print("include MIT copyright")
shutil.copyfile("../../copyright", f"{document}/copyright")
# write changelog
with open("../../changelog_template") as f:
    stringData = f.read()
# changelog, dateTime: Tue, 06 April 2018 16:32:31
t = datetime.datetime.utcnow().strftime("%a, %d %b %Y %X")
formattedString = stringData.format(DEBIANVERSION=debianVersion,DATETIME=t,VERSION=version, PACKAGENAME=packageName)
with open(f"{document}/changelog.Debian","w") as f:
    print(f"writing changelog with date utc: {t}")
    f.write(formattedString)
# by default gzip compress file in place
subprocess.run(f"gzip -9 -n {document}/changelog.Debian", shell=True)

debian = "DEBIAN"
os.makedirs(debian)
# get all files under usr/ and produce a md5 hash
print("trying to produce md5 hashes...")
subprocess.run("find usr/* -type f | xargs md5sum > DEBIAN/md5sums", shell=True)

# produce the control file from template
with open("../../control_template") as f:
    stringData = f.read()
formattedString = stringData.format(DEBIANVERSION=debianVersion, PACKAGENAME=packageName)
with open("DEBIAN/control","w") as f:
    print("trying to write control file...")
    f.write(formattedString)

# before publish
print(f"change permission of files in {os.getcwd()}")
# file permission to 644
subprocess.run("find * -type f | xargs chmod 644", shell=True)
# folder permission to 755
subprocess.run("find * -type d | xargs chmod 755", shell=True)
print(f"change bin/func permission to 755")
# octal
os.chmod("usr/bin/func", 0o755)

# go to output
os.chdir("../")
print("trying to produce deb file...")
subprocess.run(f"fakeroot dpkg-deb --build {packageName}_{debianVersion}", shell=True)

# TODO test func executables