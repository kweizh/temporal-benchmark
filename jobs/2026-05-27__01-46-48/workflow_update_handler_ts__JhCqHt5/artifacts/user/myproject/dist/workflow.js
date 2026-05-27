"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.finishSignal = exports.depositUpdate = void 0;
exports.BankBalanceWorkflow = BankBalanceWorkflow;
const workflow_1 = require("@temporalio/workflow");
const common_1 = require("@temporalio/common");
// Define the deposit Update: takes a number (amount), returns a number (new balance)
exports.depositUpdate = (0, workflow_1.defineUpdate)('deposit');
// Define the finish Signal: no arguments
exports.finishSignal = (0, workflow_1.defineSignal)('finish');
async function BankBalanceWorkflow() {
    let balance = 0;
    let finished = false;
    // Register the finish signal handler
    (0, workflow_1.setHandler)(exports.finishSignal, () => {
        finished = true;
    });
    // Register the deposit update handler with a validator
    (0, workflow_1.setHandler)(exports.depositUpdate, (amount) => {
        balance += amount;
        return balance;
    }, {
        validator: (amount) => {
            if (amount <= 0) {
                throw common_1.ApplicationFailure.create({
                    message: `Deposit amount must be positive, got: ${amount}`,
                    type: 'InvalidAmount',
                });
            }
        },
    });
    // Wait until the finish signal is received (no busy-loop)
    await (0, workflow_1.condition)(() => finished);
    return balance;
}
//# sourceMappingURL=workflow.js.map