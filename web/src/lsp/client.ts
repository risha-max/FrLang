import ReconnectingWebSocket from "reconnecting-websocket";
import type { MessageConnection } from "vscode-jsonrpc";
import {
  ConsoleLogger,
  createWebSocketConnection,
  type IWebSocket,
} from "vscode-ws-jsonrpc";
import type * as Monaco from "monaco-editor";
import {
  CompletionItem,
  Diagnostic,
  DiagnosticSeverity,
  Hover,
  InitializeParams,
  PublishDiagnosticsParams,
} from "vscode-languageserver-protocol";
import { FRLANG_DOCUMENT_URI } from "../monaco/frlang";
import { setLspBridge, type LspBridge } from "./providers";

type LspStatus = "connecting" | "ready" | "error";

function toSocket(ws: ReconnectingWebSocket): IWebSocket {
  return {
    send: (content: string) => {
      ws.send(content);
    },
    onMessage: (cb) => {
      ws.addEventListener("message", (event) => {
        const data = event.data;
        if (typeof data === "string") {
          cb(data);
          return;
        }
        if (data instanceof ArrayBuffer) {
          cb(new TextDecoder().decode(data));
          return;
        }
        if (data instanceof Blob) {
          void data.text().then(cb);
        }
      });
    },
    onError: (cb) => {
      ws.addEventListener("error", (event) => {
        cb(event);
      });
    },
    onClose: (cb) => {
      ws.addEventListener("close", (event) => {
        cb(event.code, event.reason);
      });
    },
    dispose: () => {
      ws.close();
    },
  };
}

function diagnosticMessage(message: Diagnostic["message"]): string {
  if (typeof message === "string") {
    return message;
  }
  if ("value" in message) {
    return message.value;
  }
  return String(message);
}

export class FrLangLspClient {
  private connection: MessageConnection | null = null;
  private socket: ReconnectingWebSocket | null = null;
  private model: Monaco.editor.ITextModel | null = null;
  private monaco: typeof Monaco | null = null;
  private version = 0;
  private status: LspStatus = "connecting";
  private onStatusChange: ((status: LspStatus) => void) | null = null;

  async connect(
    monaco: typeof Monaco,
    model: Monaco.editor.ITextModel,
    url: string,
    onStatus?: (status: LspStatus) => void,
  ): Promise<void> {
    this.monaco = monaco;
    this.model = model;
    this.onStatusChange = onStatus ?? null;
    this.setStatus("connecting");
    setLspBridge(null);

    this.socket = new ReconnectingWebSocket(url, [], {
      maxRetries: 12,
      connectionTimeout: 4000,
    });

    await new Promise<void>((resolve, reject) => {
      const socket = this.socket;
      if (!socket) {
        reject(new Error("WebSocket indisponible"));
        return;
      }

      const onOpen = () => {
        socket.removeEventListener("open", onOpen);
        socket.removeEventListener("error", onError);
        resolve();
      };
      const onError = () => {
        socket.removeEventListener("open", onOpen);
        socket.removeEventListener("error", onError);
        reject(new Error("Connexion LSP impossible"));
      };
      socket.addEventListener("open", onOpen);
      socket.addEventListener("error", onError);
    });

    const connection = createWebSocketConnection(
      toSocket(this.socket),
      new ConsoleLogger(),
    );
    this.connection = connection;
    connection.onNotification(
      "textDocument/publishDiagnostics",
      (params: PublishDiagnosticsParams) => {
        this.applyDiagnostics(params.diagnostics);
      },
    );
    connection.listen();

    const initParams: InitializeParams = {
      processId: null,
      clientInfo: { name: "frlang-web", version: "0.1.0" },
      capabilities: {},
      rootUri: null,
    };
    await connection.sendRequest("initialize", initParams);
    connection.sendNotification("initialized", {});

    this.version = 1;
    connection.sendNotification("textDocument/didOpen", {
      textDocument: {
        uri: FRLANG_DOCUMENT_URI,
        languageId: "frlang",
        version: this.version,
        text: model.getValue(),
      },
    });

    setLspBridge(this.createBridge(connection));
    this.setStatus("ready");
  }

  notifyChange(source: string): void {
    if (!this.connection || this.status !== "ready") {
      return;
    }
    this.version += 1;
    this.connection.sendNotification("textDocument/didChange", {
      textDocument: { uri: FRLANG_DOCUMENT_URI, version: this.version },
      contentChanges: [{ text: source }],
    });
  }

  dispose(): void {
    setLspBridge(null);
    this.connection?.dispose();
    this.connection = null;
    this.socket?.close();
    this.socket = null;
    this.model = null;
    this.monaco = null;
  }

  private createBridge(connection: MessageConnection): LspBridge {
    return {
      isReady: () => this.status === "ready",
      requestHover: (line, character) =>
        connection.sendRequest<Hover | null>("textDocument/hover", {
          textDocument: { uri: FRLANG_DOCUMENT_URI },
          position: { line, character },
        }),
      requestCompletion: (line, character) =>
        connection.sendRequest<CompletionItem[] | { items?: CompletionItem[] } | null>(
          "textDocument/completion",
          {
            textDocument: { uri: FRLANG_DOCUMENT_URI },
            position: { line, character },
          },
        ),
    };
  }

  private setStatus(status: LspStatus): void {
    this.status = status;
    this.onStatusChange?.(status);
  }

  private applyDiagnostics(diagnostics: Diagnostic[]): void {
    const monaco = this.monaco;
    const model = this.model;
    if (!monaco || !model) {
      return;
    }
    const markers = diagnostics.map((diagnostic) => ({
      severity:
        diagnostic.severity === DiagnosticSeverity.Error
          ? monaco.MarkerSeverity.Error
          : monaco.MarkerSeverity.Warning,
      message: diagnosticMessage(diagnostic.message),
      startLineNumber: diagnostic.range.start.line + 1,
      startColumn: diagnostic.range.start.character + 1,
      endLineNumber: diagnostic.range.end.line + 1,
      endColumn: diagnostic.range.end.character + 1,
    }));
    monaco.editor.setModelMarkers(model, "frlang-lsp", markers);
  }
}
