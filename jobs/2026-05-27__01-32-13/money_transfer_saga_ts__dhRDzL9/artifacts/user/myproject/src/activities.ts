import { promises as fs } from "fs";

const ACCOUNTS_PATH = "/workspace/accounts.json";

type Accounts = Record<string, number>;

async function readAccounts(): Promise<Accounts> {
  const raw = await fs.readFile(ACCOUNTS_PATH, "utf8");
  return JSON.parse(raw) as Accounts;
}

async function writeAccounts(accounts: Accounts): Promise<void> {
  await fs.writeFile(ACCOUNTS_PATH, JSON.stringify(accounts, null, 2));
}

async function updateAccount(
  account: string,
  amountDelta: number
): Promise<void> {
  const accounts = await readAccounts();
  const current = accounts[account] ?? 0;
  accounts[account] = current + amountDelta;
  await writeAccounts(accounts);
}

export async function withdraw(account: string, amount: number): Promise<void> {
  await updateAccount(account, -amount);
}

export async function deposit(account: string, amount: number): Promise<void> {
  if (account === "B_FAIL") {
    throw new Error("Simulated deposit failure for B_FAIL");
  }
  await updateAccount(account, amount);
}

export async function refund(account: string, amount: number): Promise<void> {
  await updateAccount(account, amount);
}
