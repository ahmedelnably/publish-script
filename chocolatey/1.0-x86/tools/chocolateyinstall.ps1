$ErrorActionPreference = 'Stop';

$packageName= 'azure-functions-core-tools'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://functionscdn.azureedge.net/public/1.0.11/Azure.Functions.Cli.zip'
$checksum   = '32C20C58CEDC58540C04130EBC2B4341221322A8C483A0FEE84266E01F760014906440EC6DA5F209198AC74C272842E8B7BEFBE32A940CD5D21B2C62A3158892'

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