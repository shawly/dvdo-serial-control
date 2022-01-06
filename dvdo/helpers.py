import re
import sys

import yaml
from loguru import logger

from dvdo.config import configuration

# Initialize logger
logger.remove()
logger.add(sys.stderr, level=configuration.logging.level.upper())

# Load dictionaries
settings_dict = yaml.safe_load(
    open("data/settings_dict_{lang}.yaml".format(lang=configuration.language))
)
errors_dict = yaml.safe_load(
    open("data/errors_dict_{lang}.yaml".format(lang=configuration.language))
)

# Regex patterns for parsing responses (works better than calculating byte
# lengths as responses sometimes contain the wrong data count)
reply_matcher = re.compile(
    b"\\x02(?P<cmd>(\\d)(\\d))(?P<cnt>(\\d)(\\d))(?P<set>([A-F0-9])([A-F0-9]))\\x00(?P<val>([a-zA-Z0-9_\\-\\.].*))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03"
)
error_matcher = re.compile(
    b"\\x02(?P<cmd>(\\d)(\\d))(?P<cnt>(\\d)(\\d))(?P<err>([0-9]{1,2}))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03"
)
response_matcher = re.compile(
    b"\\x02(?P<cmd>(\\d)(\\d))(?P<cnt>(\\d)(\\d))(?P<ack>([0-9]))\\x00(?P<exc>([A-F0-9])([A-F0-9]))\\x00(?P<chk>([A-F0-9])([A-F0-9]))\\x03"
)
hex_matcher = re.compile("(?P<hex>([A-F0-9])([A-F0-9]))")
value_matcher = re.compile("(?P<val>([a-zA-Z0-9_\\-\\.].*))")
