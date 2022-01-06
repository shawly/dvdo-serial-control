#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from dvdo.config import configuration
from dvdo.packet import PacketFactory, QueryPacket, ReplyPacket
from dvdo.serial import IScanSerial
from dvdo.helpers import logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device id from config.yaml')
    parser.add_argument('-u', '--uniqueid', help='unique id from settings_dict_en.yaml')
    parser.add_argument('-s', '--setting', help='raw setting id')
    args = parser.parse_args()

    device_id = args.device
    unique_id = args.uniqueid
    setting = args.setting
    # get device config from config.yaml via first param
    device = configuration.devices[device_id]

    # create serial connection
    serial = IScanSerial(device)

    # create query packet with second param (check data/settings_dict_en.yaml for possible unique_ids)
    query = PacketFactory.create_query(unique_id=unique_id, setting=setting)

    # send packet and wait for response
    answer = serial.send_and_wait_for_response(query)

    if isinstance(answer, ReplyPacket):
        answer.value

    # close connection
    serial.close()