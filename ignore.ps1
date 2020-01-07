if ([Environment]::Is64BitOperatingSystem -eq $True) {$url = "https://www.python.org/ftp/python/3.7.4/python-3.7.4-amd64.exe"}
else {$url = "https://www.python.org/ftp/python/3.7.4/python-3.7.4.exe"}


$file = $url.Split("/")[-1]

$path = "$env:TEMP\$file"

$WebClient = New-Object System.Net.WebClient
$WebClient.DownloadFile($url, $path)

Start-Process -FilePath $path -ArgumentList "/quiet InstallLauncherAllUsers=0 PrependPath=1 Include_doc=0 Include_test=0 Include_tcltk=0" -Wait





