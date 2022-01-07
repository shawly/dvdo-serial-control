# DVDOSC - DVDO iScan Serial Control

Python app to control the DVDO iScan Video Processors through an RS232 serial connection via CLI or MQTT.

| Supports | Tested |
| -------- | ------ |
| VP50 Pro | yes    |
| VP50     | no     |
| VP30     | no     |
| VP20     | no     |

Theoretically the DVDO iScan HD, HD+ and Duo could also be supported, but there was no documentation about the serial protocol or the codes so I can't guarantee that it'll work.

## Usage via CLI

```
usage: dvdosc.py [-h] [--list-settings] {query,command} ...

optional arguments:
  -h, --help       show this help message and exit
  --list-settings  lists all available settings

required arguments:
  {query,command}
    query          use query -h or --help to show usage
    command        use command -h or --help to show usage
```

### Query

```
usage: dvdosc.py query [-h] -d DEVICE (-u UNIQUEID | -s SETTING)

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        device id from config.yaml
  -u UNIQUEID, --uniqueid UNIQUEID
                        unique id from settings_dict_en.yaml
  -s SETTING, --setting SETTING
                        raw setting id
```

### Command

```
usage: dvdosc.py command [-h] -d DEVICE (-u UNIQUEID | -s SETTING) -v VALUE

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        device id from config.yaml
  -u UNIQUEID, --uniqueid UNIQUEID
                        unique id from settings_dict_en.yaml
  -s SETTING, --setting SETTING
                        raw setting id
  -v VALUE, --value VALUE
                        value for commands
```

## MQTT

Not implemented yet
