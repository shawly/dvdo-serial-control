from enum import Enum
from typing import Dict
from uuid import UUID

import yaml


class Logging:
    level: str

    def __init__(self, level: str) -> None:
        self.level = level.upper()


class Mqtt:
    server: str
    port: int
    auth: bool
    username: str
    password: str
    client_id: UUID
    discovery_topic: str

    def __init__(
        self,
        server: str,
        port: int,
        auth: bool,
        username: str,
        password: str,
        client_id: UUID,
        discovery_topic: str,
    ) -> None:
        self.server = server
        self.port = port
        self.auth = auth
        self.username = username
        self.password = password
        self.client_id = client_id
        self.discovery_topic = discovery_topic


class IScanType(Enum):
    VP50PRO = "vp50pro"
    VP50 = "vp50"
    VP30 = "vp30"
    VP20 = "vp20"
    HD = "hd"
    HDPLUS = "hdplus"
    DUO = "duo"


class Device:
    name: str
    type: IScanType
    port: str
    baudrate: int
    timeout: int

    def __init__(
        self, name: str, type: str, port: str, baudrate: int, timeout: int
    ) -> None:
        self.name = name
        self.type = IScanType(type)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout


class Config:
    language: str
    devices: Dict[str, Device]
    mqtt: Mqtt
    logging: Logging

    def __init__(
        self, language: str, devices: Dict[str, Device], mqtt: Mqtt, logging: Logging
    ) -> None:
        self.language = language
        self.devices = {}
        for key, device in devices.items():
            self.devices[key] = Device(**device)
        self.mqtt = Mqtt(**mqtt)
        self.logging = Logging(**logging)


# Load config
config_yaml = yaml.safe_load(open("config.yaml"))
configuration = Config(**config_yaml)
