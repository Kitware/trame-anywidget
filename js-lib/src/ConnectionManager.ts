import type { AnyModel } from "@anywidget/types";
import { AnyWidgetWS } from "./AnyWidgetWS";
import { updateOutputs } from "./utils";

function findFrame(parentWindow: Window, childWindow: Window) {
  const allFrames = parentWindow.document.querySelectorAll("iframe");
  for (let i = 0; i < allFrames.length; i++) {
    const frame = allFrames[i];
    if (frame.contentWindow === childWindow) {
      return frame;
    }
  }
  return null;
}

export class ConnectionManager {
  private _models: Partial<Record<string, AnyModel>>;

  constructor() {
    this._models = {};
  }

  updateCSS() {
    updateOutputs();
  }

  init(childWindow: Window, iframe: HTMLIFrameElement) {
    const frame = iframe || findFrame(window, childWindow);
    if (!frame) {
      throw new Error("No frame found for trame AnyWidget");
    }
    const serverName = frame.dataset.server || "trame";
    const clientId = frame.dataset.client;
    const model = this._models[serverName];
    if (!model) {
      throw new Error(`No model passed to AnyWidgetWS for client ${clientId}`);
    }
    return {
      createWebSocket() {
        return new AnyWidgetWS(model, clientId);
      },
    };
  }

  registerServerConnection(name: string, model: AnyModel) {
    this._models[name] = model;
  }
}
