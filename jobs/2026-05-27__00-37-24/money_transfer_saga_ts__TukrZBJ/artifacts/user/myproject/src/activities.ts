import * as fs from 'fs/promises';
import { ApplicationFailure } from '@temporalio/activity';

const ACCOUNTS_FILE = '/workspace/accounts.json';

async function readAccounts(): Promise<Record<string, number>> {
  const data = await fs.readFile(ACCOUNTS_FILE, 'utf8');
  return JSON.parse(data);
}

async function writeAccounts(accounts: Record<string, number>): Promise<void> {
  await fs.writeFile(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2));
}

export async function withdraw(account: string, amount: number): Promise<void> {
  console.log(`Withdrawing ${amount} from ${account}`);
  const accounts = await readAccounts();
  if (!accounts[account] && accounts[account] !== 0) {
    accounts[account] = 0;
  }
  accounts[account] -= amount;
  await writeAccounts(accounts);
}

export async function deposit(account: string, amount: number): Promise<void> {
  console.log(`Depositing ${amount} to ${account}`);
  if (account === 'B_FAIL') {
    throw ApplicationFailure.create({
      message: 'Intentional deposit failure for B_FAIL',
      nonRetryable: true,
    });
  }
  const accounts = await readAccounts();
  if (!accounts[account] && accounts[account] !== 0) {
    accounts[account] = 0;
  }
  accounts[account] += amount;
  await writeAccounts(accounts);
}

export async function refund(account: string, amount: number): Promise<void> {
  console.log(`Refunding ${amount} to ${account}`);
  const accounts = await readAccounts();
  if (!accounts[account] && accounts[account] !== 0) {
    accounts[account] = 0;
  }
  accounts[account] += amount;
  await writeAccounts(accounts);
}
