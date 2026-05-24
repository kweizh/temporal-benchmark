import { spawn } from 'child_process';
import * as path from 'path';

async function main() {
  console.log('Starting Worker and Client...');

  // Start the worker process
  const worker = spawn('npx', ['ts-node', 'src/worker.ts'], {
    stdio: 'inherit',
    env: process.env,
  });

  // Give the worker a few seconds to start up
  await new Promise((resolve) => setTimeout(resolve, 5000));

  // Start the client process
  const client = spawn('npx', ['ts-node', 'src/client.ts'], {
    stdio: 'inherit',
    env: process.env,
  });

  client.on('close', (code) => {
    console.log(`Client exited with code ${code}`);
    // Kill the worker when client is done
    worker.kill();
    process.exit(code || 0);
  });

  worker.on('error', (err) => {
    console.error('Worker error:', err);
  });

  client.on('error', (err) => {
    console.error('Client error:', err);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
