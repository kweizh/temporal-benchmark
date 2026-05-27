import { Context } from '@temporalio/activity';

export async function doWork(): Promise<void> {
  console.log('Activity doWork started');
  for (let i = 0; i < 60; i++) {
    Context.current().heartbeat(i);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log(`Activity doWork progress: ${i}s`);
  }
  console.log('Activity doWork completed');
}

export async function cleanup(): Promise<string> {
  console.log('Activity cleanup started');
  return 'cleanup-done';
}
