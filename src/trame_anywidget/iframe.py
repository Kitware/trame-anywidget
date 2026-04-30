import asyncio
from pathlib import Path

import anywidget
import traitlets
from loguru import logger
from trame_common.exec.asynchronous import create_task

logger.add("file_{time}.log")


class IdGenerator:
    def __init__(self, prefix="anywidget_client_"):
        self.prefix = prefix
        self.count = 0

    def next(self):
        self.count += 1
        return f"{self.prefix}{self.count}"


class GenericMessage:
    def __init__(self, data):
        self.data = data


class ServerProxy:
    def __init__(self, generic_server, anywidget):
        self._server = generic_server
        self._widget: TrameIFrame = anywidget
        self._ws = None

        anywidget.set_proxy(self)

    @property
    def id(self):
        return self._widget.client

    @property
    def endpoint(self):
        return self._server[self._server.ws_endpoints[0]]

    async def connect(self):
        logger.debug(
            "connect server {} - to model {}",
            self._widget._trame_server.name,
            self._widget.client,
        )
        self._ws = await self.endpoint.connect()
        self._ws.on_message(self.msg_server_2_widget)
        logger.debug(
            "connection done ({} <-> {})",
            self._widget._trame_server.name,
            self._ws.client_id,
        )

    async def close(self):
        if self._ws is None:
            return
        client_id = self._ws.client_id
        self._ws = None
        await self.endpoint.disconnect(client_id)

    def msg_server_2_widget(self, binary, content):
        logger.debug("msg_server_2_widget {} - {}", binary, content)
        if self._ws is None:
            return
        assert binary
        self._widget.send({"a": "s"}, [content])

    def msg_widget_2_server(self, msg, buffers):
        logger.debug("msg_widget_2_server {} - {}", msg, buffers)
        if self._ws is None:
            logger.critical("No WebSocket")
            return
        action = msg["a"]
        if action == "s":
            logger.debug("send on ws {}", buffers[0])
            self._ws.send(True, GenericMessage(buffers[0]))
        elif action == "c":
            logger.critical("Closing connection")
            create_task(self.close())
        elif action == "e":
            logger.critical("Connection error")


class TrameServerRegistry:
    def __init__(self):
        logger.debug("registry created")
        self._servers = {}  # { serverName: server }
        self._proxies = {}  # { serverName: {clientId: proxy} }

    async def start_server(self, server):
        logger.debug("start_server")
        if server.running:
            msg = "Server already running"
            raise ValueError(msg)

        logger.debug("before server start")
        server.start(
            open_browser=False,
            show_connection_info=False,
            backend="generic",
            exec_mode="task",
        )
        logger.debug("after server start")
        self._servers[server.name] = server

    async def stop_server(self, server):
        logger.debug("stop_server")
        name = server.name
        running_server = self._servers.pop(name, None)
        if running_server:
            await running_server.stop()

    async def register(self, server, anywidget):
        name = server.name
        if server.name not in self._servers:
            await self.start_server(server)

        proxy = ServerProxy(server._server, anywidget)
        self._proxies.setdefault(name, {})[proxy.id] = proxy
        await proxy.connect()

    async def unregister(self, server, anywidget):
        name = server.name
        proxies = self._proxies.get(name, {})
        proxy = proxies.pop(anywidget.client, None)

        if proxy:
            await proxy.close()

        if not proxies:
            await self.stop_server(server)


CLIENT_ID_GENERATOR = IdGenerator()
REGISTRY = TrameServerRegistry()


async def alive():
    while True:
        await asyncio.sleep(10)
        logger.debug("alive")


class TrameIFrame(anywidget.AnyWidget):
    _esm = Path(__file__).with_name("esm") / "trame-anywidget.js"
    name = traitlets.Unicode("trame").tag(sync=True)
    height = traitlets.Unicode("600px").tag(sync=True)
    ui = traitlets.Unicode("main").tag(sync=True)
    client = traitlets.Unicode("anywidget_client_default").tag(sync=True)

    def __init__(self, trame_server, ui="main", **kwargs):
        self._trame_server = trame_server
        self._proxy = None
        super().__init__(
            name=trame_server.name,
            ui=ui,
            client=CLIENT_ID_GENERATOR.next(),
            **kwargs,
        )
        self.on_msg(self._on_msg)
        create_task(REGISTRY.register(self._trame_server, self))
        create_task(alive())

        logger.debug("TrameIFrame created")

    def set_proxy(self, proxy):
        self._proxy = proxy

    def _on_msg(
        self,
        _widget: object,
        msg: object,
        buffers: list[object],
    ) -> None:
        logger.debug("_on_msg", msg, buffers)
        if self._proxy:
            logger.debug("forward to proxy")
            self._proxy.msg_widget_2_server(msg, buffers)
