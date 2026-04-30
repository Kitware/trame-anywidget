import type { RenderProps } from "@anywidget/types";
import { ConnectionManager } from "./ConnectionManager";
import { AnyWidgetProxy } from "./AnyWidgetProxy";

function render({ model, el }: RenderProps) {
  const serverName = model.get("name");
  const ui = model.get("ui");
  const clientId = model.get("client");
  const height = model.get("height");
  console.log("server name", serverName);
  console.log("server ui", ui);
  console.log("clientId", clientId);

  // Provide connection handler
  if (!(window as any).trameAnyWidget) {
    (window as any).trameAnyWidget = new ConnectionManager();
  }

  const channel = new MessageChannel();
  (window as any).trameAnyWidget.registerProxy(
    serverName,
    new AnyWidgetProxy(model, channel.port1),
  );

  // Add iframe
  const sandbox = document.createElement("iframe");
  sandbox.dataset.server = serverName;
  sandbox.dataset.client = clientId;
  sandbox.style = `border: none; width: 100%; height: ${height};`;
  sandbox.onload = () => {
    sandbox.contentWindow?.postMessage("trame-ws-channel-init", "*", [
      channel.port2,
    ]);
  };
  // sandbox.src = `https://kitware.github.io/trame-anywidget/?wsProxy=wsChannel&ui=${ui}`;
  sandbox.src = `http://localhost:8000/?wsProxy=wsChannel`;
  el.appendChild(sandbox);
}
export default { render };
