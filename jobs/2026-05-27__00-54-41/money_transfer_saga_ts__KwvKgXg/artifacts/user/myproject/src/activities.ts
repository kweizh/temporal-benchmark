import fs from 'fs/promises';

const ACCOUNTS_FILE = '/workspace/accounts.json';

async function readAccounts(): Promise<Record<string, number>> {
  const data = await fs.readFile(ACCOUNTS_FILE, 'utf-8');
  return JSON.parse(data);
}

async function writeAccounts(accounts: Record<string, number>): Promise<void> {
  await fs.writeFile(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2), 'utf-8');
}

export async function withdraw(account: string, amount: number): Promise<void> {
  const accounts = await readAccounts();
  accounts[account] = (accounts[account] || 0) - amount;
  await writeAccounts(accounts);
}

export async function deposit(account: string, amount: number): Promise<void> {
  if (account === 'B_FAIL') {
    throw new Error('Simulated deposit failure for B_FAIL');
  }
  const accounts = await readAccounts();
  accounts[account] = (accounts[account] || 0) + amount;
  await writeAccounts(accounts);
}

export async function refund(account: string, amount: number): Promise<void> {
  const accounts = await readAccounts();
  accounts[account] = (accounts[account] || 0) + amount;
  await writeAccounts(accounts);
}
