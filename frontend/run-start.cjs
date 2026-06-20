const { spawn } = require("child_process");
const path = require("path");

const port = process.env.FRONTEND_PORT || "3000";
const host = process.env.FRONTEND_HOST || "0.0.0.0";
const nextCli = path.join(__dirname, "node_modules", "next", "dist", "bin", "next");

const child = spawn(process.execPath, [nextCli, "start", "--hostname", host, "--port", port], {
  stdio: "inherit",
  shell: false,
  env: process.env,
});

child.on("exit", (code) => process.exit(code ?? 0));
