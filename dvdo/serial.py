from dvdo.config import Device
from dvdo.constants import ETX
from dvdo.packet import Packet, PacketFactory
from dvdo.helpers import logger
from serial import Serial


class IScanSerial:
    serial: Serial
    device: Device

    def __init__(self, device: Device) -> None:
        logger.info(
            "Opening connection to {name} ({type}) on port {port} with baudrate {baudrate} and timeout {timeout}...",
            name=device.name,
            type=device.type.value,
            port=device.port,
            baudrate=device.baudrate,
            timeout=device.timeout,
        )
        self.serial = Serial(
            port=device.port,
            baudrate=device.baudrate,
            rtscts=True,
            timeout=device.timeout,
        )

    def close(self):
        logger.info("Closing connection...")
        self.serial.close()

    def send(self, packet: Packet) -> None:
        logger.info("Sending packet: {packet}", packet=packet)
        self.serial.write(packet.as_bytes())

    def read(self) -> Packet:
        for response in self.serial.iread_until(ETX):
            packet = PacketFactory.create_from_response(response)
            logger.info("Received packet: {packet}", packet=packet)
            return packet
        else:
            logger.error("Timeout while receiving packet...")
            return None

    def send_and_wait_for_response(self, packet: Packet) -> Packet:
        self.send(packet)
        return self.read()
