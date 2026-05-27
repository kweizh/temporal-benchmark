import * as fs from 'fs';
import * as path from 'path';

const WORKSPACE_DIR = '/workspace';
const CHARGES_LOG = path.join(WORKSPACE_DIR, 'charges.log');

export async function chargeCard(userId: string, tier: string): Promise<void> {
  // Ensure /workspace directory exists
  if (!fs.existsSync(WORKSPACE_DIR)) {
    fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
  }

  // Append a line: <userId>:<tier>\n
  const line = `${userId}:${tier}\n`;
  fs.appendFileSync(CHARGES_LOG, line, { encoding: 'utf8' });
}

export type Activities = {
  chargeCard: typeof chargeCard;
};
