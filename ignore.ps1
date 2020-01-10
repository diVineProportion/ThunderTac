Write-Host "DETECTED PROCESSOR_ARCHITECTURE: $env:PROCESSOR_ARCHITECTURE"
$url_py37 = "https://www.python.org/ftp/python/3.7.4/python-3.7.4.exe"
if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") {  $url_py37.replace('.exe', '-amd64.exe')}
$path_file = $url_py37.Split('/')[-1]
$path_py37 = Join-Path -Path $env:TEMP -ChildPath $path_file
Write-Host "DOWNLOADING: $url_py37"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url_py37 -OutFile $path_py37
if (Test-Path $path_py37 -eq $false) {
    $WebClient = New-Object System.Net.WebClient
    $WebClient.DownloadFile($url_py37, $path_py37)
}
else { Write-Host "DOWNLOADED: $path_file" }
Write-Host "INSTALLING: $path_file"
$arguments = "/quiet PrependPath=1 InstallLauncherAllUsers=0 Include_doc=0 Include_test=0 Include_tcltk=0"
Start-Process $path_py37 $arguments -Wait
Write-Host "INSTALLED: Python 3.7.4"


