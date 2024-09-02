import asyncio

import structlog

from .connection_handler import BPQConnectionHandler, MessageType


class PlainTerminal:
    def __init__(self, connection_handler: BPQConnectionHandler):
        self.connection_handler = connection_handler
        self.logger = structlog.get_logger()

    async def run(self):
        await self.connection_handler.add_connection_status_handler(
            self.on_monitor_connection_status
        )
        await self.connection_handler.add_message_handler(self.on_recieve_data)

        while True:
            await asyncio.sleep(1)

    async def on_monitor_connection_status(self, value):
        self.logger.info("Connection status changed")
        if not value:
            self.logger.info("Disconnected")

    async def on_recieve_data(self, message):
        if message.message_type == MessageType.BPQ:
            self.logger.info(message.message)
            for port, port_name in self.connection_handler.port_info.items():
                self.logger.info(f"{port}: {port_name}")
        else:
            self.logger.info(message.message)
