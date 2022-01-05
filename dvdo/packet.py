from dvdo import constants


class Packet(object):
    def __init__(self, data_count: int, checksum=None):
        _data_count_pad = f'{data_count:02}'
        _data_count_split = list(_data_count_pad)

        self.data_count = _data_count_pad
        self.__dtc1__ = _data_count_split[0]
        self.__dtc2__ = _data_count_split[1]

        if (checksum is not None and len(checksum) == 2):
            self.checksum = checksum
            split_checksum = list(checksum)
            self.__cs1__ = split_checksum[0]
            self.__cs2__ = split_checksum[1]
        else:
            self.checksum = None
            self.__cs1__ = ''
            self.__cs2__ = ''

        self._ascii = self.as_string()
        self._bytes = self.as_bytes()
        self._hex = self.as_hex()

    @classmethod
    def fromraw(self, raw: bytes):
        self._bytes = raw
        pass

    def as_string(self) -> str:
        """Returns the packet as ASCII string"""
        if (self._bytes is not None):
            _string = self._bytes.decode()
            CHARMAP = [(constants.NULL.decode(), 'NULL'),
                       (constants.STX.decode(), 'STX'), (constants.ETX.decode(), 'ETX')]
            _map = dict((c, r) for chars, r in CHARMAP for c in list(chars))
            return ' '.join(_map.get(c, c) for c in _string)
        pass

    def as_bytes(self) -> bytes:
        """Returns the packet as bytes"""
        if (self._ascii is not None):
            _replace_whitespace = self._ascii.replace(' ', '')
            _replace_stx = _replace_whitespace.replace(
                'STX', constants.STX.decode())
            _replace_null = _replace_stx.replace(
                'NULL', constants.NULL.decode())
            _replace_etx = _replace_null.replace('ETX', constants.ETX.decode())
            return _replace_etx.encode()
        pass

    def as_hex(self) -> str:
        """Returns the packet as hex"""
        if (self._bytes is not None):
            return self._bytes.hex()
        pass


class ErrorPacket(Packet):
    def __init__(self, error_code, data_count, checksum):
        self.error_code = error_code
        try:
            self.error_description = constants.ERRORS[error_code]
        except KeyError:
            self.error_description = 'unknown'

        super().__init__(data_count, checksum)

    @classmethod
    def fromraw(self, raw: bytes):
        super().fromraw(raw)
        match = constants.ERROR_REGEX.search(raw)
        _data_count = int(match.group('cnt'))
        _error = match.group('err').decode()
        _checksum = match.group('chk').decode()
        return self(_error, _data_count, _checksum)

    def __str__(self) -> str:
        return '{self.__class__}(error_code={self.error_code}, error_description={self.error_description} data_count={self.data_count}, checksum={self.checksum})'.format(self=self)


class ResponsePacket(Packet):
    def __init__(self, acknowledge, command, data_count, checksum):
        self.acknowledge = acknowledge
        self.command = command
        super().__init__(data_count, checksum)

    @classmethod
    def fromraw(self, raw: bytes):
        super().fromraw(raw)
        match = constants.RESPONSE_REGEX.search(raw)
        _data_count = int(match.group('cnt'))
        _acknowlege = match.group('ack').decode()
        _command = match.group('exc').decode()
        _checksum = match.group('chk').decode()
        return self(_acknowlege, _command, _data_count, _checksum)

    def __str__(self) -> str:
        return '{self.__class__}(command={self.command}, acknowledge={self.acknowledge}, data_count={self.data_count}, checksum={self.checksum})'.format(self=self)


class ReplyPacket(Packet):
    def __init__(self, setting, value, data_count, checksum):
        self.setting = setting
        self.value = value
        try:
            self.setting_description = constants.SETTINGS[setting]['name']
        except KeyError:
            self.setting_description = 'unknown'
        try:
            self.value_description = constants.SETTINGS[setting]['range'][value]
        except KeyError:
            self.value_description = 'unknown'
        super().__init__(data_count, checksum)

    @classmethod
    def fromraw(self, raw: bytes):
        super().fromraw(raw)
        match = constants.REPLY_REGEX.search(raw)
        _data_count = int(match.group('cnt'))
        _setting = match.group('set').decode()
        _value = match.group('val').replace(b'\x00', b'\x5F').decode()
        _checksum = match.group('chk').decode()
        return self(_setting, _value, _data_count, _checksum)

    def __str__(self) -> str:
        return '{self.__class__}(setting={self.setting}, setting_description={self.setting_description}, value={self.value}, value_description={self.value_description}, data_count={self.data_count}, checksum={self.checksum})'.format(self=self)


class QueryPacket(Packet):
    def __init__(self, setting, checksum=None):
        if (setting is not None and len(setting) == 2):
            _split_setting = list(setting)
            self.setting = setting
            self.__id1__ = _split_setting[0]
            self.__id2__ = _split_setting[1]
        else:
            raise ValueError("setting must consist of two digits!")

        # data count is always 3 bytes so it we don't need to calculate it
        super().__init__(3, checksum)

    def __str__(self) -> str:
        return '{self.__class__}(setting={self.setting}, data_count={self.data_count}, checksum={self.checksum})'.format(self=self)

    def as_string(self) -> str:
        return 'STX 2 0 {self.__dtc1__} {self.__dtc2__} {self.__id1__} {self.__id2__} NULL {self.__cs1__}{self.__cs2__}ETX'.format(self=self)


class CommandPacket(Packet):
    def __init__(self, setting, value, checksum=None):
        if (setting is not None and len(setting) == 2):
            self.setting = setting
            _split_setting = list(setting)
            self.__id1__ = _split_setting[0]
            self.__id2__ = _split_setting[1]
        else:
            raise ValueError("setting must consist of two digits!")

        if (value is not None and len(value) == 1):
            self.value = value
        elif (value is not None and len(value) > 1):
            self.value = ' '.join(list(value))
        else:
            raise ValueError("value cannot be empty")

        # data count is value length + 4 bytes
        super().__init__(len(value) + 4, checksum)

    def __str__(self) -> str:
        return '{self.__class__}(setting={self.setting}, value={self.value}, data_count={self.data_count}, checksum={self.checksum})'.format(self=self)

    def as_string(self) -> str:
        return 'STX 3 0 {self.__dtc1__} {self.__dtc2__} {self.__id1__} {self.__id2__} NULL {self.value} NULL {self.__cs1__}{self.__cs2__}ETX'.format(self=self)


class PacketFactory:
    def __init__(self):
        return

    def create_query(self, setting, checksum=None) -> QueryPacket:
        return QueryPacket(setting, checksum)

    def create_command(self, setting, value, checksum=None) -> CommandPacket:
        return CommandPacket(setting, value, checksum)

    def create_from_response(self, raw: bytes) -> Packet:
        if (raw[0:1] != constants.STX and raw[len(raw)-1:len(raw)] != constants.ETX):
            raise ValueError(
                'invalid bytearray, it must start with STX (\x02) and end with ETX (\x03):', raw)

        _type = raw[1:3].decode()
        if (_type == constants.TYPE_REPLY_PACKET):
            return ReplyPacket.fromraw(raw)
        elif (_type == constants.TYPE_RESPONSE_PACKET):
            return ResponsePacket.fromraw(raw)
        elif (_type == constants.TYPE_ERROR_PACKET):
            return ErrorPacket.fromraw(raw)
        elif (_type == constants.TYPE_QUERY_PACKET):
            raise ValueError('why do you want to serialize a query packet?')
        elif (_type == constants.TYPE_COMMAND_PACKET):
            raise ValueError('why do you want to serialize a command packet?')
        else:
            raise ValueError('unknown type of response:', raw)
