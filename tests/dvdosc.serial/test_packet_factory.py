import unittest

from dvdosc.serial.packet_factory import ErrorPacket, PacketFactory, ReplyPacket, ResponsePacket


class TestPacketFactory(unittest.TestCase):
    def test_query_request_packet(self):
        packet = PacketFactory.create_query("A1")

        self.assertEqual(packet.as_string(), "STX 2 0 0 3 A 1 NULL ETX")
        self.assertEqual(packet.as_bytes(), b"\x022003A1\x00\x03")
        self.assertEqual(packet.as_hex(), "023230303341310003")

    def test_invalid_setting_for_query(self):
        with self.assertRaises(ValueError):
            PacketFactory.create_query("GZ")

    def test_command_request_packet_with_setting_id(self):
        packet = PacketFactory.create_command(setting="21", value="-10")

        self.assertEqual(packet.as_string(), "STX 3 0 0 7 2 1 NULL - 1 0 NULL ETX")
        self.assertEqual(packet.as_bytes(), b"\x02300721\x00-10\x00\x03")
        self.assertEqual(packet.as_hex(), "02333030373231002d31300003")

    def test_command_request_packet_with_unique_id(self):
        packet = PacketFactory.create_command(unique_id="pc_brightness", value="-10")

        self.assertEqual(packet.as_string(), "STX 3 0 0 7 2 1 NULL - 1 0 NULL ETX")
        self.assertEqual(packet.as_bytes(), b"\x02300721\x00-10\x00\x03")
        self.assertEqual(packet.as_hex(), "02333030373231002d31300003")

    def test_invalid_setting_for_command(self):
        with self.assertRaises(ValueError):
            PacketFactory.create_command("GG", "1")

    def test_invalid_value_for_command(self):
        with self.assertRaises(ValueError):
            PacketFactory.create_command("A1", "$+2/")

    def test_query_reply_packet(self):
        response_mock = b"\x022107A1\x001.2\x006D\x03"

        packet = PacketFactory.create_from_response(response_mock)

        self.assertIsInstance(packet, ReplyPacket)
        self.assertEqual(packet.as_string(), "STX 2 1 0 7 A 1 NULL 1 . 2 NULL 6 D ETX")
        self.assertEqual(packet.as_bytes(), b"\x022107A1\x001.2\x006D\x03")
        self.assertEqual(packet.as_hex(), "0232313037413100312e3200364403")

    def test_query_reply_packet_special(self):
        response_mock = b"\x022111A8\x00iScan\x00VP50Pro\x006A\x03"
        packet = PacketFactory.create_from_response(response_mock)

        self.assertIsInstance(packet, ReplyPacket)
        self.assertEqual(
            packet.as_string(),
            "STX 2 1 1 1 A 8 NULL i S c a n NULL V P 5 0 P r o NULL 6 A ETX",
        )
        self.assertEqual(packet.as_bytes(), b"\x022111A8\x00iScan\x00VP50Pro\x006A\x03")
        self.assertEqual(
            packet.as_hex(), "0232313131413800695363616e005650353050726f00364103"
        )

    def test_command_response_packet(self):
        response_mock = b"\x0201051\x0030\x005C\x03"
        packet = PacketFactory.create_from_response(response_mock)

        self.assertIsInstance(packet, ResponsePacket)
        self.assertEqual(packet.as_string(), "STX 0 1 0 5 1 NULL 3 0 NULL 5 C ETX")
        self.assertEqual(packet.as_bytes(), b"\x0201051\x0030\x005C\x03")
        self.assertEqual(packet.as_hex(), "02303130353100333000354303")

    def test_error_response_packet_one_digit(self):
        response_mock = b"\x0202022\x00F8\x03"
        packet = PacketFactory.create_from_response(response_mock)

        self.assertIsInstance(packet, ErrorPacket)
        self.assertEqual(packet.as_string(), "STX 0 2 0 2 2 NULL F 8 ETX")
        self.assertEqual(packet.as_bytes(), b"\x0202022\x00F8\x03")
        self.assertEqual(packet.as_hex(), "02303230323200463803")

    def test_error_response_packet_two_digits(self):
        response_mock = b"\x02020311\x00FD\x03"
        packet = PacketFactory.create_from_response(response_mock)

        self.assertIsInstance(packet, ErrorPacket)
        self.assertEqual(packet.as_string(), "STX 0 2 0 3 1 1 NULL F D ETX")
        self.assertEqual(packet.as_bytes(), b"\x02020311\x00FD\x03")
        self.assertEqual(packet.as_hex(), "0230323033313100464403")

    def test_unknown_packet(self):
        response_mock = b"\x02000000\x000\x0000\x03"
        with self.assertRaises(ValueError):
            PacketFactory.create_from_response(response_mock)

    def test_serialize_query_packet(self):
        response_mock = b"\x02200000\x000\x0000\x03"
        with self.assertRaises(ValueError):
            PacketFactory.create_from_response(response_mock)

    def test_serialize_command_packet(self):
        response_mock = b"\x02300000\x000\x0000\x03"
        with self.assertRaises(ValueError):
            PacketFactory.create_from_response(response_mock)

    def test_unknown_bytearray(self):
        response_mock = b"\x00"
        with self.assertRaises(ValueError):
            PacketFactory.create_from_response(response_mock)


if __name__ == "__main__":
    unittest.main()
