import { updateOutputs } from "./utils";
import type { AnyWidgetProxy } from "./AnyWidgetProxy";

export class ConnectionManager {
  private _proxies: Partial<Record<string, AnyWidgetProxy[]>>;

  constructor() {
    this._proxies = {};
  }

  updateCSS() {
    updateOutputs();
  }

  registerProxy(serverName: string, proxy: AnyWidgetProxy) {
    if (this._proxies[serverName]) {
      this._proxies[serverName].push(proxy);
    } else {
      this._proxies[serverName] = [proxy];
    }
  }
}
