
import daiquiri

from dvdo.constants import (ETX, NULL, STX, TYPE_COMMAND_PACKET,
                            TYPE_ERROR_PACKET, TYPE_QUERY_PACKET,
                            TYPE_REPLY_PACKET, TYPE_RESPONSE_PACKET,
                            UNDERSCORE)
from dvdo.utils import (config, error_matcher, errors_dict, hex_matcher,
                        reply_matcher, response_matcher, settings_dict,
                        value_matcher)

# initialize logger
daiquiri.setup(level=config["logging"]["level"].upper())
logger = daiquiri.getLogger(__name__)


class Packet(object):
    """
    The Packet object acts as a base class for all packets

    Args:
        data_count (int): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)

    Attributes:
        data_count (str): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)
        _ascii (str): Contains the packet data as ASCII string
        _bytes (bytes): Contains the packet data in bytes
        _hex (str): Contains the packet data as hex string
    """

    def __init__(self, data_count: int, checksum: str):
        _data_count_pad = f"{data_count:02}"
        _data_count_split = list(_data_count_pad)

        self.data_count = _data_count_pad
        self.__dtc1__ = _data_count_split[0]
        self.__dtc2__ = _data_count_split[1]

        if (checksum is not None and hex_matcher.match(checksum)):
            self.checksum = checksum
            split_checksum = list(checksum)
            self.__cs1__ = split_checksum[0]
            self.__cs2__ = split_checksum[1]
        else:
            self.checksum = None
            self.__cs1__ = ""
            self.__cs2__ = ""

        self._ascii = self.as_string()
        self._bytes = self.as_bytes()
        self._hex = self.as_hex()
        logger.debug("Initialized packet: %s", self)

    @classmethod
    def from_raw_response(self, raw: bytes):
        """Initializes the Packet object from raw bytes returned by the DVDO device

        Args:
            raw (bytes): A raw byte string returned from the serial connection
        """
        self._bytes = raw
        pass

    def as_string(self) -> str:
        """Returns the packet as ASCII string

        Raises:
            AttributeError: missing _bytes attribute

        Returns:
            str: packet as ASCII string
        """
        logger.debug("Returning bytes %s as ascii string", self._bytes)
        if (self._bytes is not None):
            _string = self._bytes.decode()
            CHARMAP = [(NULL.decode(), "NULL"),
                       (STX.decode(), "STX"), (ETX.decode(), "ETX")]
            _map = dict((c, r) for chars, r in CHARMAP for c in list(chars))
            return " ".join(_map.get(c, c) for c in _string)
        else:
            raise AttributeError(
                "_bytes is empty, the package has not been initialized properly")

    def as_bytes(self) -> bytes:
        """Returns the packet as bytes

        Raises:
            AttributeError: missing _ascii attribute

        Returns:
            bytes: packet as bytes
        """
        logger.debug("Returning ascii string %s as bytes", self._ascii)
        if (self._ascii is not None):
            _replace_whitespace = self._ascii.replace(" ", "")
            _replace_stx = _replace_whitespace.replace(
                "STX", STX.decode())
            _replace_null = _replace_stx.replace(
                "NULL", NULL.decode())
            _replace_etx = _replace_null.replace("ETX", ETX.decode())
            return _replace_etx.encode()
        else:
            raise AttributeError(
                "_ascii is empty, the package has not been initialized properly")

    def as_hex(self) -> str:
        """Returns the packet as hex string

        Raises:
            AttributeError: missing _bytes attribute

        Returns:
            str: packet as hex string
        """
        logger.debug("Returning bytes %s as hex string", self._bytes)
        if (self._bytes is not None):
            return self._bytes.hex()
        else:
            raise AttributeError(
                "_bytes is empty, the package has not been initialized properly")


class ErrorPacket(Packet):
    """
    ErrorPacket used for representing an error response from the serial connection

    Args:
        error_code (str): Error code of the packet
        data_count (int): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)

    Attributes:
        error_code (str): Error code of the packet
        error_description (str): A human readable description of the error
        data_count (str): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)
        _ascii (str): Contains the packet data as ASCII string
        _bytes (bytes): Contains the packet data in bytes
        _hex (str): Contains the packet data as hex string
    """

    def __init__(self, error_code, data_count, checksum):
        self.error_code = error_code
        try:
            self.error_description = errors_dict[error_code]
        except KeyError:
            self.error_description = "unknown"

        super().__init__(data_count, checksum)

    @classmethod
    def fromraw(self, raw: bytes):
        """Initializes the Packet object from raw bytes returned by the DVDO device

        Args:
            raw (bytes): A raw byte string returned from the serial connection
        """
        super().from_raw_response(raw)
        match = error_matcher.search(raw)
        _data_count = int(match.group("cnt"))
        _error = match.group("err").decode()
        _checksum = match.group("chk").decode()
        return self(_error, _data_count, _checksum)

    def __str__(self) -> str:
        return "{self.__class__}(error_code={self.error_code}, error_description={self.error_description} data_count={self.data_count}, checksum={self.checksum}, _bytes={self._bytes}, _ascii={self._ascii}, _hex={self._hex})".format(self=self)


class ResponsePacket(Packet):
    """
    ResponsePacket used for representing the response after sending a command

    Args:
        acknowledge (str): Whether the command was successful
        command (str): The command id that was sent
        data_count (int): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)

    Attributes:
        acknowledge (str): 1 when command was successful
        command (str): Always 30 because this is only returned when sending commands
        data_count (str): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)
        _ascii (str): Contains the packet data as ASCII string
        _bytes (bytes): Contains the packet data in bytes
        _hex (str): Contains the packet data as hex string
    """

    def __init__(self, acknowledge, command, data_count, checksum):
        self.acknowledge = acknowledge
        self.command = command
        super().__init__(data_count, checksum)

    @classmethod
    def fromraw(self, raw: bytes):
        """Initializes the Packet object from raw bytes returned by the DVDO device

        Args:
            raw (bytes): A raw byte string returned from the serial connection
        """
        super().from_raw_response(raw)
        match = response_matcher.search(raw)
        _data_count = int(match.group("cnt"))
        _acknowlege = match.group("ack").decode()
        _command = match.group("exc").decode()
        _checksum = match.group("chk").decode()
        return self(_acknowlege, _command, _data_count, _checksum)

    def __str__(self) -> str:
        return "{self.__class__}(command={self.command}, acknowledge={self.acknowledge}, data_count={self.data_count}, checksum={self.checksum}, _bytes={self._bytes}, _ascii={self._ascii}, _hex={self._hex})".format(self=self)


class ReplyPacket(Packet):
    """
    ReplyPacket used for representing the response after sending a query

    Args:
        setting (str): Setting id that was queried
        value (str): Value returned by the device
        data_count (int): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)

    Attributes:
        setting (str): Setting id that was queried
        value (str): Value returned by the device
        data_count (str): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)
        _ascii (str): Contains the packet data as ASCII string
        _bytes (bytes): Contains the packet data in bytes
        _hex (str): Contains the packet data as hex string
    """

    def __init__(self, setting, value, data_count, checksum):
        self.setting = setting
        self.value = value
        try:
            self.setting_description = settings_dict[setting]["name"]
        except KeyError:
            self.setting_description = ""
        try:
            self.value_description = settings_dict[setting]["range"][value]
        except KeyError:
            self.value_description = ""
        super().__init__(data_count, checksum)

    @classmethod
    def fromraw(self, raw: bytes):
        """Initializes the Packet object from raw bytes returned by the DVDO device

        Args:
            raw (bytes): A raw byte string returned from the serial connection
        """
        super().from_raw_response(raw)
        match = reply_matcher.search(raw)
        _data_count = int(match.group("cnt"))
        _setting = match.group("set").decode()
        _value = match.group("val").replace(
            NULL, UNDERSCORE).decode()
        _checksum = match.group("chk").decode()
        return self(_setting, _value, _data_count, _checksum)

    def __str__(self) -> str:
        return "{self.__class__}(setting={self.setting}, setting_description={self.setting_description}, value={self.value}, value_description={self.value_description}, data_count={self.data_count}, checksum={self.checksum}, _bytes={self._bytes}, _ascii={self._ascii}, _hex={self._hex})".format(self=self)


class QueryPacket(Packet):
    """
    QueryPacket used for reading data from the device

    Args:
        setting (str): Setting id to read
        data_count (int): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)

    Attributes:
        setting (str): Setting id to read
        data_count (str): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)
        _ascii (str): Contains the packet data as ASCII string
        _bytes (bytes): Contains the packet data in bytes
        _hex (str): Contains the packet data as hex string

    Raises:
        ValueError: When setting isn't in a proper format (e.g. two digits like "A1" or "61")
    """

    def __init__(self, setting, checksum=None):
        if (hex_matcher.match(setting)):
            _split_setting = list(setting)
            self.setting = setting
            self.__id1__ = _split_setting[0]
            self.__id2__ = _split_setting[1]
        else:
            raise ValueError("setting must consist of two digits!")

        # data count is always 3 bytes so it we don"t need to calculate it
        super().__init__(3, checksum)

    def __str__(self) -> str:
        return "{self.__class__}(setting={self.setting}, data_count={self.data_count}, checksum={self.checksum}, _bytes={self._bytes}, _ascii={self._ascii}, _hex={self._hex})".format(self=self)

    def as_string(self) -> str:
        """Returns the packet as ASCII string

        Returns:
            str: packet as ASCII string
        """
        return "STX 2 0 {self.__dtc1__} {self.__dtc2__} {self.__id1__} {self.__id2__} NULL {self.__cs1__}{self.__cs2__}ETX".format(self=self)


class CommandPacket(Packet):
    """
    CommandPacket used for sending commands to the device

    Args:
        setting (str): Setting id to set
        value (str): Value to set
        data_count (int): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)

    Attributes:
        setting (str): Setting id to set
        value (str): Value to set
        data_count (str): Contains the size of the packet
        checksum (str): Contains the checksum of the packet (optional)
        _ascii (str): Contains the packet data as ASCII string
        _bytes (bytes): Contains the packet data in bytes
        _hex (str): Contains the packet data as hex string

    Raises:
        ValueError: When setting or value aren't in a proper format (e.g. two digits for settings like "A1" or "61" and a value with a length of at least 1 which can contain digits, dashes and dots)
    """

    def __init__(self, setting, value, checksum=None):
        if (setting is not None and hex_matcher.match(setting)):
            self.setting = setting
            _split_setting = list(setting)
            self.__id1__ = _split_setting[0]
            self.__id2__ = _split_setting[1]
        else:
            raise ValueError("setting must consist of two digits!")

        if (value is not None and len(value) == 1 and value_matcher.match(value)):
            self.value = value
        elif (value is not None and len(value) > 1 and value_matcher.match(value)):
            self.value = " ".join(list(value))
        else:
            raise ValueError(
                "value has to be at least 1 byte in length and contain only letters, digits, dots or hyphens")

        # data count is value length + 4 bytes
        super().__init__(len(value) + 4, checksum)

    def __str__(self) -> str:
        return "{self.__class__}(setting={self.setting}, value={self.value}, data_count={self.data_count}, checksum={self.checksum}, _bytes={self._bytes}, _ascii={self._ascii}, _hex={self._hex})".format(self=self)

    def as_string(self) -> str:
        """Returns the packet as ASCII string

        Returns:
            str: packet as ASCII string
        """
        return "STX 3 0 {self.__dtc1__} {self.__dtc2__} {self.__id1__} {self.__id2__} NULL {self.value} NULL {self.__cs1__}{self.__cs2__}ETX".format(self=self)


class PacketFactory:
    """
    Factory for transforming raw bytes from response packets or create query and command packets for sending
    """

    def create_query(self, setting, checksum=None) -> QueryPacket:
        """Returns a QueryPacket for the given setting

        Args:
            setting (str): Setting id to query

        Returns:
            QueryPacket: a packet for querying data
        """
        logger.debug(
            "Creating query packet for setting %s with checksum %s", setting, checksum)
        return QueryPacket(setting, checksum)

    def create_command(self, setting, value, checksum=None) -> CommandPacket:
        """Returns a CommandPacket for the given setting and value

        Args:
            setting (str): Setting id to set
            value (str): Value to set for the given setting

        Returns:
            CommandPacket: a packet sending commands
        """
        logger.debug(
            "Creating command packet for setting %s with value %s and checksum %s", setting, value, checksum)
        return CommandPacket(setting, value, checksum)

    def create_from_response(self, raw: bytes) -> Packet:
        """Returns a CommandPacket for the raw data response from the device

        Args:
            raw (bytes): A raw bytes from the devices response

        Raises:
            ValueError: if either the byte array is not in the proper format or the type doesn't correspond to any packet types

        Returns:
            ReplyPacket: a packet returned after sending a QueryPacket
            ResponsePacket: a packet returned after sending a CommandPacket
            ErrorPacket: a packet returned if the device responds with an error
        """
        logger.debug("Creating packet from bytearray %s...", raw)
        if (raw[0:1] != STX and raw[len(raw)-1:len(raw)] != ETX):
            raise ValueError(
                "invalid bytearray, it must start with STX (\x02) and end with ETX (\x03):", raw)

        _type = raw[1:3].decode()
        if (_type == TYPE_REPLY_PACKET):
            logger.debug("Packet seems to be reply packet, creating instance.")
            return ReplyPacket.fromraw(raw)
        elif (_type == TYPE_RESPONSE_PACKET):
            logger.debug(
                "Packet seems to be response packet, creating instance.")
            return ResponsePacket.fromraw(raw)
        elif (_type == TYPE_ERROR_PACKET):
            logger.debug("Packet seems to be error packet, creating instance.")
            return ErrorPacket.fromraw(raw)
        elif (_type == TYPE_QUERY_PACKET):
            logger.warning(
                "Packet seems to be a query packet and should not be returned as a response!")
        elif (_type == TYPE_COMMAND_PACKET):
            logger.warning(
                "Packet seems to be a command packet and should not be returned as a response!")
        else:
            raise ValueError("unknown type of response:", raw)
