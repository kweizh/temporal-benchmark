import { proxyActivities } from "@temporalio/workflow";
import type { MoneyTransferInput } from "./types";
import type * as activities from "./activities";

const { withdraw, refund } = proxyActivities<typeof activities>({
  startToCloseTimeout: "10 seconds"
});

const { deposit } = proxyActivities<typeof activities>({
  startToCloseTimeout: "10 seconds",
  retry: {
    maximumAttempts: 2
  }
});

export async function MoneyTransfer(input: MoneyTransferInput): Promise<void> {
  const { fromAccount, toAccount, amount } = input;

  await withdraw(fromAccount, amount);

  try {
    await deposit(toAccount, amount);
  } catch (error) {
    await refund(fromAccount, amount);
    throw error;
  }
}
