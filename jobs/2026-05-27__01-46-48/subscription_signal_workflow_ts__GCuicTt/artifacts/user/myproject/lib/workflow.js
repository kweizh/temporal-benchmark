"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getStatusQuery = exports.cancelSignal = exports.upgradeSignal = void 0;
exports.SubscriptionWorkflow = SubscriptionWorkflow;
const workflow_1 = require("@temporalio/workflow");
// Define signals
exports.upgradeSignal = (0, workflow_1.defineSignal)('upgrade');
exports.cancelSignal = (0, workflow_1.defineSignal)('cancel');
// Define query
exports.getStatusQuery = (0, workflow_1.defineQuery)('getStatus');
// Proxy activities with a reasonable timeout
const { chargeCard } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '30 seconds',
});
async function SubscriptionWorkflow(input) {
    const { userId } = input;
    // Mutable state
    let tier = input.tier;
    let billings = 0;
    let cancelled = false;
    // Register signal handlers
    (0, workflow_1.setHandler)(exports.upgradeSignal, (newTier) => {
        tier = newTier;
    });
    (0, workflow_1.setHandler)(exports.cancelSignal, () => {
        cancelled = true;
    });
    // Register query handler
    (0, workflow_1.setHandler)(exports.getStatusQuery, () => ({
        tier,
        billings,
        cancelled,
    }));
    // Run up to 12 billing periods
    for (let period = 0; period < 12; period++) {
        // Check for cancellation before starting a new period
        if (cancelled) {
            break;
        }
        // Wait between periods (skip sleep before the very first period)
        if (period > 0) {
            // Sleep for 2000ms but also wake up early if cancelled
            await Promise.race([
                (0, workflow_1.sleep)(2000),
                (0, workflow_1.condition)(() => cancelled),
            ]);
            // If cancelled during sleep, exit without charging
            if (cancelled) {
                break;
            }
        }
        // Charge card for current period using the current tier
        await chargeCard(userId, tier);
        billings++;
    }
    return {
        billings,
        finalTier: tier,
        cancelled,
    };
}
//# sourceMappingURL=workflow.js.map