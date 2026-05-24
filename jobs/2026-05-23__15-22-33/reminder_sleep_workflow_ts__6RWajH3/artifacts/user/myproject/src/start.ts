import { spawn } from 'child_process';
import * as path from 'path';

async function main() {
  // Start the worker
  const worker = spawn('npx', ['ts-node', path.join(__dirname, 'worker.ts')], {
    stdio: 'inherit',
    env: process.env,
  });

  // Give worker a moment to start
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Run the client
  const client = spawn('npx', ['ts-node', path.join(__dirname, 'client.ts')], {
    stdio: 'inherit',
    env: process.env,
  });

  client.on('close', (code) => {
    // Kill the worker when the client finishes
    worker.kill();
    process.exit(code || 0);
  });

  worker.on('error', (err) => {
    console.error('Worker failed to start:', err);
    client.kill();
    process.exit(1);
  });
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
