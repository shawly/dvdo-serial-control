
import yaml
import re

# load config
_config = yaml.safe_load(open('config.yaml'))
_lang = _config['global']['lang']

# ASCII Codes that are returned over serial
NULL = b'\x00'
STX = b'\x02'
ETX = b'\x03'
UNDERSCORE = b'\x5F'

# Regex patterns for parsing responses (works better than calculating byte lengths as responses sometimes contain the wrong data count)
REPLY_REGEX = re.compile(b'\\x02(?P<cmd>(\d)(\d))(?P<cnt>(\d)(\d))(?P<set>([A-F0-9])([A-F0-9]))\\x00(?P<val>([a-zA-Z0-9_\-\.].*))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03')
ERROR_REGEX = re.compile(b'\\x02(?P<cmd>(\d)(\d))(?P<cnt>(\d)(\d))(?P<err>([0-9])([0-9]))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03')
RESPONSE_REGEX = re.compile(b'\\x02(?P<cmd>(\d)(\d))(?P<cnt>(\d)(\d))(?P<ack>([0-9]))\\x00(?P<exc>([A-F0-9])([A-F0-9]))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03')

# Load dictionaries
SETTINGS = yaml.safe_load(open('data/settings_dict_{lang}.yaml'.format(lang=_lang)))
ERRORS = yaml.safe_load(open('data/errors_dict_{lang}.yaml'.format(lang=_lang)))

# Type codes for packets
TYPE_RESPONSE_PACKET = '01'
TYPE_ERROR_PACKET = '02'
TYPE_QUERY_PACKET = '20'
TYPE_REPLY_PACKET = '21'
TYPE_COMMAND_PACKET = '30'