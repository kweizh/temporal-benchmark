import fs from 'fs/promises';
import path from 'path';

export async function chargeCard(userId: string, tier: string): Promise<void> {
  const workspacePath = '/workspace';
  const filePath = path.join(workspacePath, 'charges.log');
  
  await fs.mkdir(workspacePath, { recursive: true });
  await fs.appendFile(filePath, `${userId}:${tier}\n`);
}
