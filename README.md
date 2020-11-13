# Prusa Mini Integration for Home Assistant
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fsq3tle%2Fprusa_mini_home_assistant&count_bg=%2379C83D&title_bg=%23555555&icon=github.svg&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

This integration allows you to get current state of the printer via API used by Prusa Connect Web Interface. Customizable pooling time and values to monitor.


### Manual instalation

  
  - Create custom_components folder in your config folder (there is configuration.yaml located)
  - Create prusa_connect folder inside custom_components
  - Get repository 
  - Unpack */custom_components/prusa_connect* to */config/custom_components/prusa_connect* 
  - Add entry in configuration.yaml as below
  - Restart Home Assistant

### HACS instalation

  - Add "https://github.com/sq3tle/prusa_mini_home_assistant" into Custom repositories
  - Install via HACS
  - Add entry in configuration.yaml
  - Restart Home Assistant


### Configuration
Add lines shown below into your *configuration.yaml*
Remeber to set printer IP and choose what conditions you want to monitor in HA.
```yaml
sensor:
 - platform: prusa_connect
   host: 10.10.0.5          # set printer ip
   name: Prusa Mini         
   scan_interval: 30         # set refresh interval (seconds)
   monitored_conditions:
    - status                # return printer state: printing, online, offline, cooling, heating
    - temp_nozzle           # return nozzle temperature
    - temp_bed              # return bed temperature
    - material              # return current loaded material
    - progress              # return printing progress 0-100
    - time_est              # return estimated time to complete (minutes)
    - project_name          # return printing job filename
    - pos_z_mm              # return z height in mm (floating point)
    - time_tts              # return time readable by google assistant
```



