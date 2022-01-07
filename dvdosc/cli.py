#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys

from prettytable import PrettyTable
from prettytable.prettytable import ALL, MARKDOWN

from dvdosc.config import configuration
from dvdosc.helpers import logger, settings_dict
from dvdosc.serial.iscan_serial import IScanSerial
from dvdosc.serial.packet_factory import (
    ErrorPacket,
    Packet,
    PacketFactory,
    ReplyPacket,
    ResponsePacket,
)


def send_query(args):
    device_id = args.device
    unique_id = args.uniqueid
    setting = args.setting
    packet = PacketFactory.create_query(unique_id=unique_id, setting=setting)
    send_packet(device_id, packet)


def send_command(args):
    device_id = args.device
    unique_id = args.uniqueid
    setting = args.setting
    value = args.value
    packet = PacketFactory.create_command(
        unique_id=unique_id, setting=setting, value=value
    )
    send_packet(device_id, packet)


def send_packet(device_id: str, packet: Packet):
    errorcode = 0

    # get device config from config.yaml via first param
    device = configuration.devices[device_id]
    # create serial connection
    serial = IScanSerial(device)

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
        errorcode = answer.error_code

    # close connection
    serial.close()
    return errorcode


def print_settings():
    t = PrettyTable(
        ["Setting", "Unique ID", "Name", "Group", "Permission (read/write)", "Range"]
    )
    for key, setting in settings_dict.items():
        perm = setting["permission"]
        range = setting["range"] if "range" in setting and "w" in perm else ""
        if isinstance(range, list):
            range = " - ".join([str(i) for i in range])
        if isinstance(range, dict):
            range = "\n".join(
                [str(key + " = " + val["name"]) for key, val in range.items()]
            )
        t.add_row(
            [
                key,
                setting["unique_id"],
                setting["name"],
                setting["group"],
                ",".join(perm),
                range,
            ]
        )

    t.set_style(MARKDOWN)
    print(t.get_string(sortby="Group", hrules=ALL))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title="required arguments")

    query_parser = subparsers.add_parser(
        "query", help="use query -h or --help to show usage"
    )
    query_parser.add_argument(
        "-d", "--device", help="device id from config.yaml", required=True
    )
    query_setting_args = query_parser.add_mutually_exclusive_group(required=True)
    query_setting_args.add_argument(
        "-u", "--uniqueid", help="unique id from settings_dict_en.yaml"
    )
    query_setting_args.add_argument("-s", "--setting", help="raw setting id")
    query_parser.set_defaults(func=send_query)

    command_parser = subparsers.add_parser(
        "command", help="use command -h or --help to show usage"
    )
    command_parser.add_argument(
        "-d", "--device", help="device id from config.yaml", required=True
    )
    command_setting_args = command_parser.add_mutually_exclusive_group(required=True)
    command_setting_args.add_argument(
        "-u", "--uniqueid", help="unique id from settings_dict_en.yaml"
    )
    command_setting_args.add_argument("-s", "--setting", help="raw setting id")
    command_parser.add_argument(
        "-v", "--value", help="value for commands", required=True
    )
    command_parser.set_defaults(func=send_command)

    parser.add_argument("--list-settings", help="lists all available settings", action="store_true")

    args = parser.parse_args()
    if hasattr(args, "func"):
        sys.exit(args.func(args))
    elif args.list_settings:
        print_settings()
    else:
        parser.print_help()
