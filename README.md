# ThunderTac  
###### (THIS README IS AN INCOMPLETE WORK IN PROGRESS)

![](https://raw.githubusercontent.com/diVineProportion/ThunderTac/master/resources/thundertac_white_400.png)  


 
## CONFIGURATION (config.ini)

<details>
 
 - Location: `%LOCALAPPDATA%\WarThunderApps\ThunderTac\update\config.ini`
 - Access: `ThunderTac.exe --config 1`



|categ\|y|key|value|description|notes|
|--|--|--|--|--|
netw\|k | source_ip | `127.0.0.1` \| `localhost` \| `192.168.xxx.xxx` | address to access the telemetry | PS4 / XBO directions below
netw\|k | source_pt | `8111 `| port to access the telemetry | don't change this unless you know what you are doing| 
general | ttac_usr |  `diVineProption` | name displayed in tacview | must match in-game name |
general | ttac_mas |  `diVineProption` | host of the session | must match in-game name | 
general | ttac_rec |  `ttac.rec` | chat cmd to start rec | must match exactly |
~~general~~ | ~~ttac_end~~ |  ~~`ttac.end`~~ | ~~chat cmd to end rec~~ | DISABLED |
loguru | level |  `CRITICAL` \| `WARNING` \| `DEBUG` \| `INFO` | level of msgs that show in cmd window | `INFO` for the least |
debug | debug_on |  `True` \| `False` | automatic recording start in mp battles | for single player recording |
ftpcred | ftp_send |  `True` \| `False` | Submit zipped recording | Avoid having to send file to host (for merging) manually
ftpcred | ftp_addr |  `address` | ftp submission adress (working public sample provided) | don't include the protocol `ftp://` |
ftpcred | ftp_user |  `username` \| `anonymous` | ftp username credentials | not sure if anonymous works for you ftp server |
ftpcred | ftp_pass |  `passw\|d` \| `None` | ftp password credentials | leave blank for ftp with anonymous logins  |
ftpcred | ftp_sess |  `/some/remote/path` | path on remote directory | easier to find your you session
pyupdater | channel |  `stable` \|  `beta` \| `alpha` | release channel | stable safest |
pyupdater | strict |  `True` \| `False` | stay on set channel | set False for all updates 
configinit | first_run |  `True` \| `False` | first time running | soon depreciated |


# </details>

## Platform Information  

<details>  

##### PC  
+ Windows  
  + \#PCMasterRace  
  
+ LINUX:   
  + Progress: 80% Completed  
  + Testers needed  
+ MAC:  
  + lol  
##### CONSOLE  
  
  
+ PS4*:  
  + Get PS4 IP Address:  
      + `PS4 Settings` &#8594; `Network` &#8594; `View Connection Status` &#8594; `IP Address`  
 + Update `client.ini`  
 + Under the `[network]` category, replace `source_ip` with the `IP Address`   
+ It should be `192.168.xxx.xxx`  
  
+ XBO:  
  + I have no idea with XBO. If you know someone with XBO that's interested, send them my way.  
      
      
> \* I began working with someone on PS4 to see if it outputs the web interface (this is what is needed for the data)  
and we were able to verify that the PS4 does output the map, but we weren't able to do a proper test. I am fairly  
confident that this works, but don't hold me to it. You will need a laptop or computer on the **same network** as the PS4.

</details>

  ### TODO
 - [x] Solo Test Flight
 - [x] Multiplayer Recordings
 - [ ] Solo Test Flight (Real-time)
 - [ ] Multiplayer Recordings (Real-time)
 - [x] Automatic Submissions (FTP)
 - [ ] Automatic Merging
 - [ ] Helicopters (Full Telemetry)
 - [ ] Tank and Ship (Simple Telemetry)
