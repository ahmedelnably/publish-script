$ErrorActionPreference = 'Stop';

$packageName= 'azure-functions-core-tools'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://functionscdn.azureedge.net/public/2.0.1-beta.25/Azure.Functions.Cli.win-x86.2.0.1-beta.25.zip'
$checksum 	= '49A54FA96D8FDC32BDDE691B4977CEEAF708D4B38AE4C4E75B1913BC1D59CC8E5714FF09FB5EB990928558FF8C48FCFD89DCE309E3544168A077FCA8E3A96613'

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