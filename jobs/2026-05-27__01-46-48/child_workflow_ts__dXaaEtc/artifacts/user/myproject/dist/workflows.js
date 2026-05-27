"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DoubleWorkflow = DoubleWorkflow;
exports.ParentSumWorkflow = ParentSumWorkflow;
const workflow_1 = require("@temporalio/workflow");
/**
 * DoubleWorkflow accepts a single number `n` and returns `n * 2`.
 */
async function DoubleWorkflow(n) {
    return n * 2;
}
/**
 * ParentSumWorkflow accepts an array of numbers, invokes DoubleWorkflow
 * once per element via executeChild, and returns the sum of all doubled values.
 */
async function ParentSumWorkflow(numbers) {
    const doubled = await Promise.all(numbers.map((n, index) => (0, workflow_1.executeChild)(DoubleWorkflow, {
        args: [n],
        taskQueue: 'child-workflow-ts',
        workflowId: `child-double-${index}-${n}`,
    })));
    return doubled.reduce((sum, val) => sum + val, 0);
}
//# sourceMappingURL=workflows.js.map