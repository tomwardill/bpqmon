import asyncio
import threading

import click

from .connection_handler import BPQConnectionHandler
from .fancy_terminal import BPQMonApp
from .plain_terminal import PlainTerminal
from .mqtt import MQTTOutput


# coroutine that will start another coroutine after a delay in seconds
async def delay(coro, seconds):
    # suspend for a time limit in seconds
    await asyncio.sleep(seconds)
    # execute the other coroutine
    await coro()


async def start_listeners(
    fancy_terminal, plain_terminal, host, port, username, password, mqtt_details: dict
):
    if plain_terminal and fancy_terminal:
        raise ValueError("Cannot run in both plain and fancy terminal mode")

    connection_handler = BPQConnectionHandler(
        hostname=host, port=port, username=username, password=password
    )
    asyncio.create_task(delay(connection_handler.connect, 5))
    await asyncio.sleep(1)

    outputs = []

    if fancy_terminal:
        app = BPQMonApp(connection_handler=connection_handler)

        async def run_app() -> None:
            """Run the app."""
            app._loop = asyncio.get_running_loop()
            app._thread_id = threading.get_ident()
            try:
                await app.run_async(
                    headless=False,
                    inline=False,
                    inline_no_clear=False,
                    mouse=True,
                    size=None,
                    auto_pilot=None,
                )
            finally:
                app._loop = None
                app._thread_id = 0

        outputs.append(run_app)
    elif plain_terminal:
        terminal = PlainTerminal(connection_handler)
        outputs.append(terminal.run)
    if mqtt_details["enabled"]:
        del mqtt_details["enabled"]
        mqtt = MQTTOutput(connection_handler, **mqtt_details)
        outputs.append(mqtt.run)
    if not outputs:
        raise NotImplementedError("Other modes not implemented yet")

    await asyncio.gather(*[output() for output in outputs])


@click.command()
@click.option(
    "--fancy-terminal", is_flag=True, default=False, help="Run in ~fancy~ terminal mode"
)
@click.option(
    "--plain-terminal", is_flag=True, default=False, help="Run in plain terminal mode"
)
@click.option("--host", default="localhost", help="Host to connect to")
@click.option("--port", default=8011, help="Port to connect to")
@click.option("--mqtt", is_flag=True, default=False, help="Enable MQTT output")
@click.option("--mqtt-hostname", default="localhost", help="MQTT host to connect to")
@click.option("--mqtt-port", default=1883, help="MQTT port to connect to")
@click.option("--mqtt-username", default="", help="MQTT username")
@click.option("--mqtt-password", default="", help="MQTT password")
@click.argument("username")
@click.argument("password")
def run(
    fancy_terminal,
    plain_terminal,
    host,
    port,
    mqtt,
    mqtt_hostname,
    mqtt_port,
    mqtt_username,
    mqtt_password,
    username,
    password,
):
    mqtt_details = {
        "enabled": mqtt,
        "hostname": mqtt_hostname,
        "port": mqtt_port,
        "username": mqtt_username,
        "password": mqtt_password,
    }

    # Get into asyncio world
    asyncio.run(
        start_listeners(
            fancy_terminal, plain_terminal, host, port, username, password, mqtt_details
        )
    )


if __name__ == "__main__":
    run()
