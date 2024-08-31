import asyncio
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    BPQ = 255
    ACTIVITY = b"\x1b"


@dataclass
class BPQMessage:
    message_type: MessageType
    message: str
    port: int


class BPQConnectionHandler:
    _is_connected = False
    _reader = None
    _writer = None

    port_info = {}

    @property
    def is_connected(self):
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value):
        print("Setting is_connected")
        self._is_connected = value
        if self.on_connection_status:
            self.on_connection_status(value)

    def __init__(
        self,
        hostname,
        port,
        username,
        password,
        on_connection_status=None,
        on_message=None,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self.on_connection_status = on_connection_status
        self.on_message = on_message

    async def _get_oneshot_data(self):
        while True:
            data = await self._reader.read(1024)
            if len(data) == 0:
                pass
            return data

    async def connect(self):
        print("Connecting")
        self._reader, self._writer = await asyncio.open_connection(
            self.hostname, self.port
        )

        connection_string = f"{self.username}\r{self.password}\rBPQTERMTCP\r\n"
        print(connection_string.encode())
        self._writer.write(connection_string.encode())

        data = await self._get_oneshot_data()
        if b"Connected to TelnetServer" in data:
            self.is_connected = True
            print("Connected")

        self._writer.write(b"\\\\\\\\8000000000000003 1 1 0 1 0 0 1\r")
        while True:
            data = await self._get_oneshot_data()
            print(data)
            if self.on_message:
                message = self.parse_message(data)
                self.on_message(message)

    def parse_message(self, data):
        header, message = data[0:2], data[2:]
        message_type = MessageType(header[1])
        bpq_message = BPQMessage(message_type, message.decode(), 0)

        if bpq_message.message_type == MessageType.BPQ:
            port_info = bpq_message.message.split("|")[1:-1]
            for port in port_info:
                print(port)
                port_number, port_description = port.split(" ", 1)
                self.port_info[int(port_number)] = port_description

        return bpq_message
