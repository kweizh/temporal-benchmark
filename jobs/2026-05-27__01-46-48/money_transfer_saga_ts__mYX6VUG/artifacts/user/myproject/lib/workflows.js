"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MoneyTransfer = MoneyTransfer;
const workflow_1 = require("@temporalio/workflow");
// Proxy for withdraw and refund: generous retries are fine
const { withdraw, refund } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '30 seconds',
    retry: {
        maximumAttempts: 3,
    },
});
// Proxy for deposit: limit attempts so the failure path terminates quickly
const { deposit } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '30 seconds',
    retry: {
        maximumAttempts: 1,
    },
});
/**
 * MoneyTransfer saga workflow.
 *
 * Happy path  → withdraw → deposit → COMPLETED
 * Failure path → withdraw → deposit (fails) → refund → re-throw → FAILED
 */
async function MoneyTransfer(input) {
    const { fromAccount, toAccount, amount } = input;
    // Step 1: debit the source account
    await withdraw(fromAccount, amount);
    // Step 2: credit the destination account; compensate on failure
    try {
        await deposit(toAccount, amount);
    }
    catch (err) {
        // Compensation: refund the source account so its balance is restored
        await refund(fromAccount, amount);
        // Re-surface the original error so the workflow reaches FAILED status.
        // Wrap in ApplicationFailure so Temporal records it cleanly.
        if (err instanceof workflow_1.ActivityFailure && err.cause instanceof workflow_1.ApplicationFailure) {
            throw workflow_1.ApplicationFailure.fromError(err.cause, { message: `Deposit failed; refund issued. Original: ${err.cause.message}` });
        }
        throw err;
    }
}
//# sourceMappingURL=workflows.js.map