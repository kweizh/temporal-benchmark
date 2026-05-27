import * as fs from 'fs';

export async function doStep(i: number): Promise<void> {
  fs.appendFileSync('/workspace/progress.log', `step ${i}\n`);
}