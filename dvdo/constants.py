
import json
import re

NULL = b'\x00'
STX = b'\x02'
ETX = b'\x03'

REPLY_REGEX = re.compile(b'\\x02(?P<cmd>(\d)(\d))(?P<cnt>(\d)(\d))(?P<set>([A-F0-9])([A-F0-9]))\\x00(?P<val>([a-zA-Z0-9_\-\.].*))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03')
ERROR_REGEX = re.compile(b'\\x02(?P<cmd>(\d)(\d))(?P<cnt>(\d)(\d))(?P<err>([0-9])([0-9]))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03')
RESPONSE_REGEX = re.compile(b'\\x02(?P<cmd>(\d)(\d))(?P<cnt>(\d)(\d))(?P<ack>([0-9]))\\x00(?P<exc>([A-F0-9])([A-F0-9]))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03')

SETTINGS = json.load(open('data/settings_dict_en.json'))
ERRORS = json.load(open('data/errors_dict_en.json'))

TYPE_RESPONSE_PACKET = '01'
TYPE_ERROR_PACKET = '02'
TYPE_QUERY_PACKET = '20'
TYPE_REPLY_PACKET = '21'
TYPE_COMMAND_PACKET = '30'