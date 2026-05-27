import { promises as fs } from "fs";

export async function doStep(step: number): Promise<void> {
  await fs.appendFile("/workspace/progress.log", `step ${step}\n`);
}
