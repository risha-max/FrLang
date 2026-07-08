import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: 0,
  use: {
    baseURL: process.env.FRLANG_WEB_URL ?? "http://127.0.0.1:5173",
    trace: "on-first-retry",
  },
  webServer: process.env.FRLANG_SKIP_WEBSERVER
    ? undefined
    : {
        command: "bash ../scripts/web-dev.sh",
        url: "http://127.0.0.1:5173",
        reuseExistingServer: true,
        timeout: 120_000,
      },
});
