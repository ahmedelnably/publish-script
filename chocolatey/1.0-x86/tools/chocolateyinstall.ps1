$ErrorActionPreference = 'Stop';

$packageName= 'azure-functions-core-tools'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://functionscdn.azureedge.net/public/1.0.9/Azure.Functions.Cli.zip'
$checksum 	= '8803F46F6B3F467BDF401FBA0EFB6E08644A1DF77434BEC65159512BB68A3579B37BE9A09E8B54591BC6973FC63AE17D64D7A7484B383EAE8F670CC25053DC8E'

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