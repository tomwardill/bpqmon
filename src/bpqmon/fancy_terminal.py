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

    def __init__(self, connection_handler: BPQConnectionHandler):
        self.connection_handler = connection_handler
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield RichLog(markup=True, id="log")
            with Horizontal(id="footer"):
                yield Static("Connecting...", id="connectionLabel", classes="box")
                yield Static("No port info", classes="box")

    async def on_mount(self) -> None:
        await self.connection_handler.add_connection_status_handler(
            self.on_monitor_connection_status
        )
        await self.connection_handler.add_message_handler(self.on_recieve_data)

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
