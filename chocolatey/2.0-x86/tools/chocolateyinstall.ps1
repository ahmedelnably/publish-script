$ErrorActionPreference = 'Stop';

$packageName= 'azure-functions-core-tools'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url        = 'https://functionscdn.azureedge.net/public/2.0.1-beta.26/Azure.Functions.Cli.win-x86.2.0.1-beta.26.zip'
$checksum   = 'B536E75B02DD67F676A2EEA877157867F600171B02395592652485BEFE6177B6CD1B34028F76449F73CFB9B8B2B535E218E3C7AA58B846D1FF8D93B285864AAC'

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