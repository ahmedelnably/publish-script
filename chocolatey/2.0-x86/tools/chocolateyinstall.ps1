$ErrorActionPreference = 'Stop';

$packageName= 'azure-functions-core-tools'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://functionscdn.azureedge.net/public/2.0.1-beta.29/Azure.Functions.Cli.win-x86.2.0.1-beta.29.zip'
$checksum   = '9B722835D7C16F8F48DA61C8C61A683F6C934AA7A7F3761B56AA86BD04193444A6BC0B8E02117CE8634DF8ABF2BE79CE75BEFDD7F475B24CA00D0E7B6B16665F'

$packageArgs = @{
  packageName   = $packageName
  unzipLocation = $toolsDir
  url           = $url
  checksum      = $checksum
  checksumType  = 'SHA512'
}

Install-ChocolateyZipPackage @packageArgs

# only symlink for func.exe
$files = get-childitem $toolsDir -include *.exe -recurse
foreach ($file in $files) {
  if (!$file.Name.Equals("func.exe")) {
    #generate an ignore file
    New-Item "$file.ignore" -type file -force | Out-Null
  }
}