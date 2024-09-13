import asyncio

import paho.mqtt.client as mqtt
import structlog

from .connection_handler import BPQConnectionHandler, MessageType


class MQTTOutput:
    def __init__(
        self,
        connection_handler: BPQConnectionHandler,
        hostname: str,
        port: int,
        username: str,
        password: str,
    ):
        self.connection_handler = connection_handler
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.logger = structlog.get_logger().bind(output="mqtt")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.logger.info(f"Connected with result code {reason_code}")

    async def run(self):
        self.logger.info("Starting MQTT output")
        await self.connection_handler.add_connection_status_handler(
            self.on_monitor_connection_status
        )
        await self.connection_handler.add_message_handler(self.on_recieve_data)

        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc = mqttc
        self.mqttc.on_connect = self.on_connect
        self.mqttc.username_pw_set(self.username, self.password)
        self.mqttc.connect(self.hostname, self.port)

        self.mqttc.loop_start()
        self.logger.info("MQTT Loop started")
        while True:
            await asyncio.sleep(1)

    async def on_monitor_connection_status(self, value):
        pass

    async def on_recieve_data(self, message):
        if message.message_type == MessageType.BPQ:
            self.mqttc.publish("bpq/log", message.message)
            for port, port_name in self.connection_handler.port_info.items():
                self.mqttc.publish(f"bpq/port/{port}", f"{port_name}")
        else:
            self.mqttc.publish(f"bpq/port/{message.port}", message.message)
