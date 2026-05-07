export async function withdraw(accountId: string, amount: number): Promise<void> {
  console.log(`Withdrawing ${amount} from account ${accountId}`);
}

export async function deposit(accountId: string, amount: number): Promise<void> {
  if (accountId === 'fail') {
    console.error(`Deposit to account ${accountId} failed as requested`);
    throw new Error('Deposit failed');
  }
  console.log(`Depositing ${amount} to account ${accountId}`);
}

export async function refund(accountId: string, amount: number): Promise<void> {
  console.log(`Refunding ${amount} to account ${accountId}`);
}
