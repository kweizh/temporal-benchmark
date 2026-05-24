import * as fs from 'fs';
import * as path from 'path';

export async function chargeCard(userId: string, tier: string): Promise<void> {
  const workspaceDir = '/workspace';
  const logFile = path.join(workspaceDir, 'charges.log');

  if (!fs.existsSync(workspaceDir)) {
    fs.mkdirSync(workspaceDir, { recursive: true });
  }

  fs.appendFileSync(logFile, `${userId}:${tier}\n`);
}
