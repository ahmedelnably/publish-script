$ErrorActionPreference = 'Stop';

$packageName= 'azure-functions-core-tools'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://functionscdn.azureedge.net/public/2.0.1-beta.31/Azure.Functions.Cli.win-x86.2.0.1-beta.31.zip'
$checksum   = '8256D779B262751B612B1835B9754CBF5545098AA3CACDE0FD49423697E0D043417FD79D2D7D93791879E4EE17A4044CF0872661C0D2032EC753AADAD66E5A4D'

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