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


CLIENT_ID_GENERATOR = IdGenerator()


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
