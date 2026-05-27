import { spawn } from 'child_process';
import * as path from 'path';

async function run() {
  console.log('Starting Worker and Client...');

  const worker = spawn('npx', ['ts-node', 'src/worker.ts'], {
    stdio: 'inherit',
    env: process.env,
  });

  // Give the worker a few seconds to start up
  await new Promise((resolve) => setTimeout(resolve, 5000));

  const client = spawn('npx', ['ts-node', 'src/client.ts'], {
    stdio: 'inherit',
    env: process.env,
  });

  client.on('close', (code) => {
    console.log(`Client exited with code ${code}`);
    worker.kill();
    process.exit(code || 0);
  });

  worker.on('error', (err) => {
    console.error('Worker error:', err);
  });
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
