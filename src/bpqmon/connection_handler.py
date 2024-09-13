import asyncio
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    BPQ = 255
    ACTIVITY = 27


@dataclass
class BPQMessage:
    message_type: MessageType
    message: str
    port: int


class BPQConnectionHandler:
    is_connected = True
    _idle_task = None
    _reader = None
    _writer = None

    connection_status_handlers = []
    message_handlers = []

    port_info = {}

    def __init__(
        self,
        hostname,
        port,
        username,
        password,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    async def add_connection_status_handler(self, handler):
        self.connection_status_handlers.append(handler)

    async def add_message_handler(self, handler):
        self.message_handlers.append(handler)

    async def _get_oneshot_data(self):
        while True:
            data = await self._reader.read(1024)
            if len(data) == 0:
                pass
            return data

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(
            self.hostname, self.port
        )

        connection_string = f"{self.username}\r{self.password}\rBPQTERMTCP\r\n"
        self._writer.write(connection_string.encode())

        data = await self._get_oneshot_data()
        if b"Connected to TelnetServer" in data:
            self.is_connected = True
            await asyncio.gather(
                *[handler(True) for handler in self.connection_status_handlers]
            )
            self._idle_task = asyncio.create_task(self.idle_loop())

        self._writer.write(b"\\\\\\\\8000000000000003 1 1 0 1 0 0 1\r")
        while True:
            data = await self._get_oneshot_data()
            message = self.parse_message(data)
            await asyncio.gather(
                *[handler(message) for handler in self.message_handlers]
            )

    async def idle_loop(self):
        while True:
            if self.is_connected:
                self._writer.write(b"\0")
            await asyncio.sleep(5 * 60)

    def parse_message(self, data):
        header, message = data[0:2], data[2:]
        message_type = MessageType(header[1])
        content = message.decode(errors="ignore").strip()
        bpq_message = BPQMessage(message_type, content, 0)

        if bpq_message.message_type == MessageType.BPQ:
            port_info = bpq_message.message.split("|")[1:-1]
            for port in port_info:
                port_number, port_description = port.split(" ", 1)
                self.port_info[int(port_number)] = port_description
        elif bpq_message.message_type == MessageType.ACTIVITY:
            bpq_message.message = bpq_message.message[1:]

            if "Port=" not in bpq_message.message:
                return bpq_message

            port = int(bpq_message.message.split("Port=")[1].split(" ")[0])
            bpq_message.port = port

        return bpq_message
