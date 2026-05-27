export interface TransferInput {
    fromAccount: string;
    toAccount: string;
    amount: number;
}
/**
 * MoneyTransfer saga workflow.
 *
 * Happy path  → withdraw → deposit → COMPLETED
 * Failure path → withdraw → deposit (fails) → refund → re-throw → FAILED
 */
export declare function MoneyTransfer(input: TransferInput): Promise<void>;
//# sourceMappingURL=workflows.d.ts.map