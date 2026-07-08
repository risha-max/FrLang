import { expect, test } from "@playwright/test";

const APP_URL = process.env.FRLANG_WEB_URL ?? "http://127.0.0.1:5173";

test.describe("Atelier FrLang", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await expect(page.locator(".status")).toHaveText("LSP : ready", {
      timeout: 15_000,
    });
  });

  test("affiche Hello World après exécution", async ({ page }) => {
    const hello = 'afficher "Bonjour le monde!";';
    await page.evaluate(async (source) => {
      await fetch("/api/main", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });
    }, hello);
    await page.reload();
    await expect(page.locator(".status")).toHaveText("LSP : ready", {
      timeout: 15_000,
    });

    await page.getByRole("button", { name: "Exécuter" }).click();
    await expect(page.locator(".output")).toContainText("Bonjour le monde!", {
      timeout: 10_000,
    });
    await expect(page.locator(".output.error")).toHaveCount(0);
  });

  test("affiche une erreur de syntaxe via LSP", async ({ page }) => {
    const invalid = "soit nombre x = ;\nafficher x;";
    await page.evaluate(async (source) => {
      await fetch("/api/main", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });
    }, invalid);
    await page.reload();
    await expect(page.locator(".status")).toHaveText("LSP : ready", {
      timeout: 15_000,
    });

    await expect(page.locator(".squiggly-error")).toHaveCount(1, {
      timeout: 10_000,
    });
  });

  test("retourne la documentation hover pour un mot-clé", async ({ page }) => {
    const hover = await page.evaluate(async () => {
      return new Promise<string>((resolve) => {
        const ws = new WebSocket(
          `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/lsp`,
        );
        const uri = "file:///main.frlang";
        const source = "afficher x;";

        ws.onopen = () => {
          ws.send(
            JSON.stringify({
              jsonrpc: "2.0",
              id: 1,
              method: "initialize",
              params: { processId: null, capabilities: {}, rootUri: null },
            }),
          );
        };

        ws.onmessage = async (event) => {
          const text =
            typeof event.data === "string"
              ? event.data
              : await event.data.text();
          const message = JSON.parse(text) as {
            id?: number;
            result?: { contents?: { value?: string } };
          };

          if (message.id === 1) {
            ws.send(JSON.stringify({ jsonrpc: "2.0", method: "initialized", params: {} }));
            ws.send(
              JSON.stringify({
                jsonrpc: "2.0",
                method: "textDocument/didOpen",
                params: {
                  textDocument: {
                    uri,
                    languageId: "frlang",
                    version: 1,
                    text: source,
                  },
                },
              }),
            );
            ws.send(
              JSON.stringify({
                jsonrpc: "2.0",
                id: 2,
                method: "textDocument/hover",
                params: {
                  textDocument: { uri },
                  position: { line: 0, character: 3 },
                },
              }),
            );
          }

          if (message.id === 2) {
            resolve(message.result?.contents?.value ?? "");
            ws.close();
          }
        };

        setTimeout(() => resolve(""), 8_000);
      });
    });

    expect(hover).toContain("afficher");
    expect(hover.toLowerCase()).toMatch(/affiche|sortie/);
  });

  test("ne documente pas les variables utilisateur", async ({ page }) => {
    const hover = await page.evaluate(async () => {
      return new Promise<string | null>((resolve) => {
        const ws = new WebSocket(
          `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/lsp`,
        );
        const uri = "file:///main.frlang";
        const source = "soit nombre x = 1;";

        ws.onopen = () => {
          ws.send(
            JSON.stringify({
              jsonrpc: "2.0",
              id: 1,
              method: "initialize",
              params: { processId: null, capabilities: {}, rootUri: null },
            }),
          );
        };

        ws.onmessage = async (event) => {
          const text =
            typeof event.data === "string"
              ? event.data
              : await event.data.text();
          const message = JSON.parse(text) as {
            id?: number;
            result?: { contents?: { value?: string } } | null;
          };

          if (message.id === 1) {
            ws.send(JSON.stringify({ jsonrpc: "2.0", method: "initialized", params: {} }));
            ws.send(
              JSON.stringify({
                jsonrpc: "2.0",
                method: "textDocument/didOpen",
                params: {
                  textDocument: {
                    uri,
                    languageId: "frlang",
                    version: 1,
                    text: source,
                  },
                },
              }),
            );
            ws.send(
              JSON.stringify({
                jsonrpc: "2.0",
                id: 2,
                method: "textDocument/hover",
                params: {
                  textDocument: { uri },
                  position: { line: 0, character: 12 },
                },
              }),
            );
          }

          if (message.id === 2) {
            resolve(message.result?.contents?.value ?? null);
            ws.close();
          }
        };

        setTimeout(() => resolve(null), 3_000);
      });
    });

    expect(hover).toBeNull();
  });

  test("propose l'autocomplétion des mots-clés", async ({ page }) => {
    await page.evaluate(async () => {
      await fetch("/api/main", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: "" }),
      });
    });
    await page.reload();
    await expect(page.locator(".status")).toHaveText("LSP : ready", {
      timeout: 15_000,
    });

    const editor = page.locator(".monaco-editor");
    await editor.click();
    await page.keyboard.type("aff");
    await page.keyboard.press("Control+Space");

    await expect(page.locator(".monaco-list-row").first()).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.locator(".monaco-list-row")).toContainText(["afficher"]);
  });
});
