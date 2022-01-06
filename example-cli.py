#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys

from dvdo.config import configuration
from dvdo.packet_handler import ErrorPacket, PacketFactory, ReplyPacket, ResponsePacket
from dvdo.iscan_serial import IScanSerial
from dvdo.helpers import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--device", help="device id from config.yaml", required=True
    )
    parser.add_argument("-u", "--uniqueid", help="unique id from settings_dict_en.yaml")
    parser.add_argument("-s", "--setting", help="raw setting id")
    parser.add_argument(
        "-c", "--command", help="command type (query or command)", required=True
    )
    parser.add_argument("-v", "--value", help="value for commands")
    args = parser.parse_args()

    device_id = args.device
    unique_id = args.uniqueid
    setting = args.setting
    command = args.command
    value = args.value
    errorcode = 0
    # get device config from config.yaml via first param
    device = configuration.devices[device_id]

    # create serial connection
    serial = IScanSerial(device)

    packet = None
    # create query packet with second param (check data/settings_dict_en.yaml for possible unique_ids)
    if command == "query":
        packet = PacketFactory.create_query(unique_id=unique_id, setting=setting)
    elif command == "command":
        packet = PacketFactory.create_command(
            unique_id=unique_id, setting=setting, value=value
        )

    # send packet and wait for response
    answer = serial.send_and_wait_for_response(packet)

    if isinstance(answer, ReplyPacket):
        logger.info(
            "Setting {setting} ({setting_raw}) is set to {value} ({value_raw})",
            setting_raw=answer.setting,
            setting=answer.setting_description,
            value_raw=answer.value,
            value=answer.value_description,
        )
    if isinstance(answer, ResponsePacket):
        logger.info(
            "Command was execution was {value}!",
            value="successful" if answer.acknowledge == "1" else "unsuccessful",
        )
    if isinstance(answer, ErrorPacket):
        logger.error(
            "Device responded with error: {error} ({error_code})",
            error=answer.error_description,
            error_code=answer.error_code,
        )
        errorcode=answer.error_code

    # close connection
    serial.close()
    sys.exit(errorcode)
