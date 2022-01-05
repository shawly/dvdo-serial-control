# ASCII Codes that are returned over serial
NULL = b'\x00'
STX = b'\x02'
ETX = b'\x03'
UNDERSCORE = b'\x5F'

# Type codes for packets
TYPE_RESPONSE_PACKET = '01'
TYPE_ERROR_PACKET = '02'
TYPE_QUERY_PACKET = '20'
TYPE_REPLY_PACKET = '21'
TYPE_COMMAND_PACKET = '30'
