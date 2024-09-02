import asyncio
import threading

import click

from .connection_handler import BPQConnectionHandler
from .fancy_terminal import BPQMonApp


# coroutine that will start another coroutine after a delay in seconds
async def delay(coro, seconds):
    # suspend for a time limit in seconds
    await asyncio.sleep(seconds)
    # execute the other coroutine
    await coro()


async def start_listeners(
    fancy_terminal, plain_terminal, host, port, username, password
):
    if plain_terminal and fancy_terminal:
        raise ValueError("Cannot run in both plain and fancy terminal mode")

    connection_handler = BPQConnectionHandler(
        hostname=host, port=port, username=username, password=password
    )
    asyncio.create_task(delay(connection_handler.connect, 5))
    await asyncio.sleep(1)

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

        await run_app()
    elif plain_terminal:
        raise NotImplementedError("Plain terminal mode not implemented yet")
    else:
        raise NotImplementedError("Other modes not implemented yet")


@click.command()
@click.option(
    "--fancy-terminal", is_flag=True, default=False, help="Run in ~fancy~ terminal mode"
)
@click.option(
    "--plain-terminal", is_flag=True, default=False, help="Run in plain terminal mode"
)
@click.option("--host", default="localhost", help="Host to connect to")
@click.option("--port", default=8011, help="Port to connect to")
@click.argument("username")
@click.argument("password")
def run(fancy_terminal, plain_terminal, host, port, username, password):
    # Get into asyncio world
    asyncio.run(
        start_listeners(fancy_terminal, plain_terminal, host, port, username, password)
    )


if __name__ == "__main__":
    run()
