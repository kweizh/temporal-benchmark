import { Context } from '@temporalio/activity';

export async function doWork(): Promise<void> {
  const ctx = Context.current();
  for (let i = 0; i < 60; i++) {
    await ctx.sleep(1000);
    ctx.heartbeat();
  }
}

export async function cleanup(): Promise<string> {
  return 'cleanup-done';
}
