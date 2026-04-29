import type { RenderProps } from "@anywidget/types";
import { ConnectionManager } from "./ConnectionManager";

function render({ model, el }: RenderProps) {
  const serverName = model.get("name");
  const ui = model.get("ui");
  const clientId = model.get("client");
  const height = model.get("height");
  console.log("server name", serverName);
  console.log("server ui", ui);
  console.log("clientId", clientId);

  // Provide connection handler
  if (!(window as any).trameJupyter) {
    (window as any).trameJupyter = new ConnectionManager();
  }
  (window as any).trameJupyter.registerServerConnection(serverName, model);

  // Add iframe
  const sandbox = document.createElement("iframe");
  sandbox.dataset.server = serverName;
  sandbox.dataset.client = clientId;
  sandbox.style = `border: none; width: 100%; height: ${height};`;
  el.appendChild(sandbox);

  console.log("iframe", sandbox);
  console.log("iframe.contentWindow", sandbox.contentWindow);

  sandbox.onload = () => {
    console.log("iframe.contentWindow (loaded)", sandbox.contentWindow);
    (sandbox.contentWindow as any).WSLINK = (window as any).trameJupyter.init(
      sandbox.contentWindow,
      sandbox,
    );
  };
  sandbox.src = `https://kitware.github.io/trame-anywidget/?ui=${ui}`;
}
export default { render };
