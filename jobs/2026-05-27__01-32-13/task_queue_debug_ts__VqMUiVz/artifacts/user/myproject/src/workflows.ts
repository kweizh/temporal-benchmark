export async function PingWorkflow(name: string): Promise<string> {
  return `pong-${name}`;
}
