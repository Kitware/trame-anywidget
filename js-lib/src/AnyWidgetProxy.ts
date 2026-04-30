import type { AnyModel } from "@anywidget/types";

export class AnyWidgetProxy {
  constructor(model: AnyModel, connection: MessagePort) {
    connection.onmessage = (e: MessageEvent) => {
      const { a, b, c, t } = e.data;
      const msg = { a };
      if (c) Object.assign(msg, { c });
      if (t) Object.assign(msg, { t });
      console.log("trame msg:", msg, [b]);
      model.send(msg, null, [b]);
      console.log("trame msg - sent");
    };
    model.on("msg:custom", (msg, buffers) => {
      console.log("widget msg:", msg, buffers);
      connection.postMessage({ ...msg, b: buffers[0] }, buffers);
    });
    console.log("create fake WS proxy", model, connection);
  }
}
