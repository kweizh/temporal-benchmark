import { spawn } from 'child_process';
import path from 'path';

async function run() {
  const workerProcess = spawn('npx', ['ts-node', path.join(__dirname, 'worker.ts')], {
    stdio: 'inherit',
    env: process.env,
  });

  // Give the worker a moment to start
  await new Promise(resolve => setTimeout(resolve, 2000));

  const clientProcess = spawn('npx', ['ts-node', path.join(__dirname, 'client.ts')], {
    stdio: 'inherit',
    env: process.env,
  });

  clientProcess.on('close', (code) => {
    workerProcess.kill();
    process.exit(code || 0);
  });
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
