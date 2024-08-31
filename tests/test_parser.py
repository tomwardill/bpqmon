from bpqmon.connection_handler import BPQConnectionHandler, BPQMessage, MessageType


def test_bpq_message():
    bpq_message = BPQMessage(message_type=MessageType.BPQ, message="Hello", port=1)
    assert bpq_message.message_type == MessageType.BPQ
    assert bpq_message.message == "Hello"
    assert bpq_message.port == 1


def test_parsing_management_message():
    bpq_connection_handler = BPQConnectionHandler(
        hostname=None, port=None, username=None, password=None
    )
    bpq_message = bpq_connection_handler.parse_message(
        b"\xff\xff4|0 Mail Monitor|1 VHF Packet 1200-baud|2 HF Packet BPSK300|9 Telnet|"
    )
    assert bpq_message.message_type == MessageType.BPQ
    assert (
        bpq_message.message
        == "4|0 Mail Monitor|1 VHF Packet 1200-baud|2 HF Packet BPSK300|9 Telnet|"
    )
    assert bpq_message.port == 0

    assert bpq_connection_handler.port_info == {
        0: "Mail Monitor",
        1: "VHF Packet 1200-baud",
        2: "HF Packet BPSK300",
        9: "Telnet",
    }
