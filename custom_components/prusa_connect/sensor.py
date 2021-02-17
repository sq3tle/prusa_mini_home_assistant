from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL, CONF_MONITORED_CONDITIONS
from homeassistant.helpers.entity import Entity
from datetime import timedelta

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import requests

"""
EXAMPLE OF configuration.yaml

sensor:
 - platform: prusa_connect
   host: 10.10.0.5
   name: Prusa Mini
   scan_interval: 2
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
"""

SCAN_INTERVAL = timedelta(seconds=60)

# Available conditions to monitor
S_AVAILABLE = ['status', 'temp_nozzle', 'temp_bed', 'material', 'progress', 'time_est', 'project_name', 'pos_z_mm','time_tts']
META = {'status':[None,'mdi:printer-3d'], 'temp_nozzle':['°C','mdi:printer-3d-nozzle-outline'], 'temp_bed':['°C','mdi:approximately-equal-box'], 'material':['','mdi:bullseye'], 'progress':['%','mdi:file-percent'], 'time_est':[' m','mdi:timer-sand'], 'project_name':[None,'mdi:file'], 'pos_z_mm':[' mm','mdi:format-align-justify'],'time_tts':[None,'mdi:timer-sand']}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {   # handle config and its validation
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): vol.All(cv.time_period, cv.positive_timedelta),
        vol.Optional(CONF_MONITORED_CONDITIONS, default=S_AVAILABLE): vol.All(cv.ensure_list, [vol.In(S_AVAILABLE)])
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    # register sensor to home assistant backend
    backend = PrusaApi(config.get(CONF_NAME), config.get(CONF_HOST))
    add_entities([PrusaSensor(hass, name, backend) for name in config.get(CONF_MONITORED_CONDITIONS)], True)


class PrusaSensor(Entity):
    def __init__(self, hass, name, inst):
        # setup home assistant sensor instance

        self.inst = inst
        self.v_name = name
        # self._hass = hass

    @property
    def name(self):
        # return sensor name to home assistant
        return "{}_{}".format(self.inst.name, self.v_name)

    @property
    def state(self):
        # return sensor value to home assistant
        return self.inst.attributes.get(self.v_name, None)

    @property
    def icon(self):
        # return icon to home assistant frontend
        return META[self.v_name][1]

    @property
    def unit_of_measurement(self):
        # return unit to home assistant frontend
        return META[self.v_name][0]

    def update(self):
        # request backend upgrade, but only when called from one instance
        if 'status' == self.v_name:
            self.inst.update()


class PrusaApi:
    def __init__(self, name, host):
        # just class setup
        self.host = host
        self.name = name
        self.attributes = {}
        self.tracked = ['temp_nozzle', 'temp_bed', 'material', 'pos_z_mm', 'printing_speed',
                        'flow_factor', 'progress', 'print_dur', 'project_name', 'time_est']

    def update(self):
        # gather new values from Prusa Connect interface into self.attributes
        try:
            response = requests.get("http://{}/api/telemetry".format(str(self.host)), timeout=1)
            response = response.json()
            self.attributes = {'status': 'online'}
        except requests.exceptions.ConnectTimeout:
            response = {}
            self.attributes = {'status': 'offline'}

        for atr in self.tracked:
            self.attributes[atr] = response.get(atr, None)

        if self.attributes['project_name']:
            if float(self.attributes['pos_z_mm']) == 0.0:
                self.attributes['status'] = 'heating'
            else:
                self.attributes['status'] = 'printing'
                self.attributes['time_est'] = int(self.attributes['time_est']) // 60
                self.attributes['time_tts'] = str(self.time_to_tts_readable(int(self.attributes['time_est'])))
        elif self.attributes['temp_nozzle'] and 50 <= int(self.attributes['temp_nozzle']):
            self.attributes['status'] = 'cooling'
          
    @staticmethod
    def time_to_tts_readable(x):
        mins = x % 60
        hours = x // 60
        days = x // 1440
        hours -= days * 24
        if days:
            return '{}d {}h {}m'.format(days, hours, mins)
        elif hours:
            return '{}h {}m'.format(hours, mins)
        else:
            return '0h {}m'.format(mins)
