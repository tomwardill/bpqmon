import asyncio

import click
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, RichLog

from .connection_handler import BPQConnectionHandler, BPQMessage, MessageType


PORT_COLOURS = [
    "red",
    "green",
    "darkblue",
    "yellow",
    "magenta",
    "cyan",
]


class BPQMonApp(App):
    CSS_PATH = "layout.tcss"
    connection_handler = None

    def __init__(self, host=None, port=None, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield RichLog(markup=True, id="log")
            with Horizontal(id="footer"):
                yield Static("Connecting...", id="connectionLabel", classes="box")
                yield Static("No port info", classes="box")

    async def on_mount(self) -> None:
        self.connection_handler = BPQConnectionHandler(
            self.host,
            self.port,
            self.username,
            self.password,
            on_connection_status=self.on_monitor_connection_status,
            on_message=self.on_recieve_data,
        )
        self.reader_task = asyncio.create_task(self.connection_handler.connect())
        await asyncio.sleep(0)

    async def on_monitor_connection_status(self, value):
        self.log("Connection status changed")
        footer = self.query_one("#footer")
        footer.remove_children()
        if not value:
            await footer.mount(Static("Disconnected", classes="box"))

    async def on_recieve_data(self, message: BPQMessage):
        self.log(message.message)
        log_view = self.query_one("#log")
        if message.message_type == MessageType.BPQ:
            log_view.write(f"[bold]{message.message}")

            # Update footer with port info
            footer = self.query_one("#footer")
            print(self.connection_handler.port_info)
            for port, port_name in self.connection_handler.port_info.items():
                print(port, port_name)
                await footer.mount(
                    Static(f"{port}: {port_name}", classes=f"box port_{port}")
                )

        else:
            log_view.write(f"[{PORT_COLOURS[message.port]}]{message.message}")


@click.command()
@click.option("--terminal", is_flag=True, default=True, help="Run in terminal mode")
@click.option("--host", default="localhost", help="Host to connect to")
@click.option("--port", default=8011, help="Port to connect to")
@click.argument("username")
@click.argument("password")
def run(terminal, host, port, username, password):
    if terminal:
        app = BPQMonApp(host=host, port=port, username=username, password=password)
        app.run()
    else:
        raise NotImplementedError("Other modes not implemented yet")


if __name__ == "__main__":
    run()
