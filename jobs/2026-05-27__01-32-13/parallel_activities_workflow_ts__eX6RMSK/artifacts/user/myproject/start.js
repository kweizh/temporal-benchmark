const { spawn } = require("child_process");

const worker = spawn("npm", ["run", "worker"], {
  stdio: "inherit",
  shell: process.platform === "win32",
});

const startClient = () =>
  new Promise((resolve) => {
    const client = spawn("npm", ["run", "client"], {
      stdio: "inherit",
      shell: process.platform === "win32",
    });

    client.on("exit", (code) => {
      resolve(code ?? 0);
    });
  });

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
  try {
    await delay(2000);
    const code = await startClient();
    worker.kill();
    process.exit(code);
  } catch (error) {
    worker.kill();
    console.error(error);
    process.exit(1);
  }
})();
