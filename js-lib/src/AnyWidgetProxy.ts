import type { AnyModel } from "@anywidget/types";

export class AnyWidgetProxy {
  constructor(model: AnyModel, connection: MessagePort) {
    console.log("create fake WS proxy", model, connection);
  }
}
