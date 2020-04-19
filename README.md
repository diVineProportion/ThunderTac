# ThunderTac  (THIS README IS AN INCOMPLETE WORK IN PROGRESS)
![](https://raw.githubusercontent.com/diVineProportion/ThunderTac/master/resources/thundertac_black_400.png)  
  

## config.ini
**[network]**  
source_ip = [ `127.0.0.1` | `localhost` | `192.168.xxx.xxx`  ]
source_pt = [ `8111`  ]
**[general]**  
ttac_usr = [ `diVineProportion`]   
ttac_mas = [ `diVineProportion` ]   
ttac_rec = ttac.rec  
**[loguru]**  
level = DEBUG  
**[debug]**  
debug_on = False  
**[ftpcred]**  
ftp_send = True  
ftp_addr = ftp.thundertac.altervista.org  
ftp_user = thundertac  
ftp_pass = c63sghaFEP58  
ftp_sess = WIP  
**[pyupdater]**  
channel = 1  
**[configinit]**  
first_run = False

## Platform Information  
  
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
