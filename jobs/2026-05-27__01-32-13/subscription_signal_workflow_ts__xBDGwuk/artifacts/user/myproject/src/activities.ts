import { promises as fs } from 'node:fs';

const chargesDir = '/workspace';
const chargesFile = `${chargesDir}/charges.log`;

export async function chargeCard(userId: string, tier: string): Promise<void> {
  await fs.mkdir(chargesDir, { recursive: true });
  await fs.appendFile(chargesFile, `${userId}:${tier}\n`, 'utf8');
}
