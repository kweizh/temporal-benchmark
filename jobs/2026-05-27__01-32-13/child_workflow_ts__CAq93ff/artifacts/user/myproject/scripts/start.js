const { spawn } = require('child_process');

const workerProcess = spawn('npm', ['run', 'worker'], {
  stdio: 'inherit',
  env: process.env,
});

let shuttingDown = false;

const stopWorker = () => {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;
  workerProcess.kill('SIGTERM');
};

const runClient = () =>
  new Promise((resolve, reject) => {
    const clientProcess = spawn('npm', ['run', 'client'], {
      stdio: 'inherit',
      env: process.env,
    });

    clientProcess.on('exit', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Client exited with code ${code}`));
      }
    });

    clientProcess.on('error', reject);
  });

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
  try {
    await delay(2000);
    await runClient();
    stopWorker();
  } catch (error) {
    console.error(error);
    stopWorker();
    process.exit(1);
  }
})();

process.on('SIGINT', () => {
  stopWorker();
  process.exit(1);
});

process.on('SIGTERM', () => {
  stopWorker();
  process.exit(1);
});
