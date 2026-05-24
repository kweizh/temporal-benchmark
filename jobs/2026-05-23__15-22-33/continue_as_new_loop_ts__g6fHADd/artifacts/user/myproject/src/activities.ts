import * as fs from 'fs';
import * as path from 'path';

const LOG_PATH = '/workspace/loop.log';

export async function incrementCounter(currentValue: number): Promise<number> {
  const next = currentValue + 1;
  fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
  fs.appendFileSync(LOG_PATH, `${next}\n`);
  return next;
}
