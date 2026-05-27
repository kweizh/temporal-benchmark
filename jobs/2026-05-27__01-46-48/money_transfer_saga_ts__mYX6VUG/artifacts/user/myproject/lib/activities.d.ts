/**
 * Subtract `amount` from `accounts[account]`.
 */
export declare function withdraw(account: string, amount: number): Promise<void>;
/**
 * Add `amount` to `accounts[account]`.
 * If `account === "B_FAIL"`, throw a non-retryable error to simulate failure.
 */
export declare function deposit(account: string, amount: number): Promise<void>;
/**
 * Add `amount` back to `accounts[account]` — reverses a prior withdraw.
 */
export declare function refund(account: string, amount: number): Promise<void>;
//# sourceMappingURL=activities.d.ts.map