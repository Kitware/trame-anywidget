import type { AnyModel } from "@anywidget/types";

type WebsocketMessage<T> = { data: T };
type CommMessage = {
  data: any;
  buffers?: ArrayBuffer[] | ArrayBufferView[];
};

function noOp() {}

function toBuffer(msgpack: any) {
  if (msgpack.buffer) {
    if (msgpack.buffer.byteLength !== msgpack.length) {
      console.warn("toBuffer: deep copy");
      const tmp = new Uint8Array(msgpack.length);
      tmp.set(msgpack);
      return tmp.buffer;
    }
    return msgpack.buffer;
  }
  return msgpack;
}

export class AnyWidgetWS {
  private _model: AnyModel;
  private _clientId: string;
  private _on_open: (data: any) => void;
  private _on_error: (data: any) => void;
  private _on_close: (data: any) => void;
  private _on_msg: (data: WebsocketMessage<any>) => void;

  constructor(model: AnyModel, clientId: string | undefined) {
    console.log("create fake WS");
    this._model = model;
    this._clientId = clientId || "missing_client_id";
    this._on_open = noOp;
    this._on_error = noOp;
    this._on_close = noOp;
    this._on_msg = noOp;

    // FIXME need to bind model.on_msg => _on_msg
  }

  send(data: string | ArrayBufferLike | ArrayBufferView) {
    const isBinary = typeof data !== "string";

    const message: CommMessage = {
      data: {
        client: this._clientId,
      },
      buffers: [],
    };

    if (isBinary) {
      message.buffers = [toBuffer(data)];
    } else {
      message.data.payload = data;
    }

    this._model.send(message.data, null, message.buffers);
  }

  set onopen(callback: (data: any) => void) {
    this._on_open = callback;
    console.log("on open", this._on_open);
  }

  set onmessage(callback: (data: WebsocketMessage<any>) => void) {
    this._on_msg = callback;
    console.log("on message", this._on_msg);
  }

  set onclose(callback: (data: any) => void) {
    this._on_close = callback;
    console.log("on close", this._on_close);
  }

  set onerror(callback: (data: any) => void) {
    this._on_error = callback;
    console.log("on error", this._on_error);
  }
}
