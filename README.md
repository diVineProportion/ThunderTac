# ThunderTac  
### (THIS README IS AN INCOMPLETE WORK IN PROGRESS)
![](https://raw.githubusercontent.com/diVineProportion/ThunderTac/master/resources/thundertac_white_400.png)  
  

## config.ini explained
```
[network]
```
net_host = `[ 127.0.0.1 | localhost | 192.168.xxx.xxx ]`

net_port = `[ 8111 ]`

```
[general]
```

**ttac_usr** = [ player's name ]` must match in-game name

ttac_mas = `[ hosters name ]`

ttac_rec = `[ any string ] `

```
[loguru]
```

level = `[ CRITICAL | WARNING | DEBUG | INFO ]`

```
[debug]
```

debug_on = `[ True | False ]`

```
[ftpcred]
```

ftp_send = `[ True | False ]`

ftp_addr = `[ any ftp address ]`

ftp_user = `[ ftp user credential ]`

ftp_pass = `[ ftp pass credential ]`

ftp_sess = `[ ftp folder name ]`

```
[pyupdater]
```

channel = `[ stable | beta | alpha ]`

strict = `[ True | False ]`

```
[configinit]
```

first_run = `[ True | False ]`


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
