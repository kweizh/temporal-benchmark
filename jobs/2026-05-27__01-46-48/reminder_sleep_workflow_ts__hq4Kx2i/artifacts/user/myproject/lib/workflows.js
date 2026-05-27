"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReminderWorkflow = ReminderWorkflow;
const workflow_1 = require("@temporalio/workflow");
// Proxy the Notify activity with a reasonable timeout
const { Notify } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '30 seconds',
});
/**
 * ReminderWorkflow: sleeps for delaySeconds, then calls Notify and returns its result.
 */
async function ReminderWorkflow(input) {
    const { message, delaySeconds } = input;
    // Deterministic sleep inside the workflow sandbox
    await (0, workflow_1.sleep)(delaySeconds * 1000);
    // Invoke the Notify activity and return the result
    return await Notify(message);
}
//# sourceMappingURL=workflows.js.map