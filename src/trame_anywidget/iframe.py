import asyncio
from pathlib import Path

import anywidget
import traitlets
from loguru import logger

logger.add("file_{time}.log")


class IdGenerator:
    def __init__(self, prefix="anywidget_client_"):
        self.prefix = prefix
        self.count = 0

    def next(self):
        self.count += 1
        return f"{self.prefix}{self.count}"


class TrameServerRegistry:
    def __init__(self):
        self._servers = {}
        self._widgets = {}

    async def start_server(self, server):
        if server.running:
            msg = "Server already running"
            raise ValueError(msg)

        rs = server.start(
            open_browser=False,
            show_connection_info=False,
            backend="generic",
        )
        self._servers[server.name] = server
        print(f"{rs=}", server)

    async def stop_server(self, server):
        name = server.name
        running_server = self._servers.pop(name, None)
        if running_server:
            await running_server.stop()

    async def register(self, server, anywidget):
        name = server.name
        self._widgets.setdefault(name, []).append(anywidget)
        if server.name in self._servers:
            return

        # start generic server
        await self.start_server(server)

    async def unregister(self, server, anywidget):
        name = server.name
        server_widgets = self._widgets.get(name, set())
        server_widgets.discard(anywidget)
        if not server_widgets:
            await self.stop_server(server)


CLIENT_ID_GENERATOR = IdGenerator()
REGISTRY = TrameServerRegistry()


class TrameIFrame(anywidget.AnyWidget):
    _esm = Path(__file__).with_name("esm") / "trame-anywidget.js"
    name = traitlets.Unicode("trame").tag(sync=True)
    height = traitlets.Unicode("600px").tag(sync=True)
    ui = traitlets.Unicode("main").tag(sync=True)
    client = traitlets.Unicode("anywidget_client_default").tag(sync=True)

    def __init__(self, trame_server, ui="main", **kwargs):
        self._trame_server = trame_server
        super().__init__(
            name=trame_server.name,
            ui=ui,
            client=CLIENT_ID_GENERATOR.next(),
            **kwargs,
        )

        self._task = asyncio.create_task(REGISTRY.register(self._trame_server, self))

        # print(dir(self))
        self.on_msg(self._handle_custom_message)

    def _handle_custom_message(
        self,
        _widget: object,
        msg: object,
        buffers: list[object],
    ) -> None:
        logger.debug("msg {}", msg)
        logger.debug("buffers {}", buffers)
