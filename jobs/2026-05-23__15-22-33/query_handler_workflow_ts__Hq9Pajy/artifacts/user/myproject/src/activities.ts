import * as fs from 'fs';
import * as path from 'path';

export async function doStep(i: number): Promise<void> {
  const logPath = '/workspace/progress.log';
  fs.appendFileSync(logPath, `step ${i}\n`);
}
