import fs from 'node:fs';

export async function Notify(message: string): Promise<string> {
  const line = `Notified: ${message}`;
  fs.mkdirSync('/workspace', { recursive: true });
  fs.appendFileSync('/workspace/reminder.log', `${line}\n`);
  return line;
}
