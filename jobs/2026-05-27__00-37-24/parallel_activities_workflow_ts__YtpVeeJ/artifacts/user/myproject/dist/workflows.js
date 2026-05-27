"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ParallelSquaresWorkflow = ParallelSquaresWorkflow;
const workflow_1 = require("@temporalio/workflow");
const { squareNumber } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '1 minute',
});
async function ParallelSquaresWorkflow(numbers) {
    const promises = numbers.map((n) => squareNumber(n));
    const results = await Promise.all(promises);
    return results.reduce((sum, n) => sum + n, 0);
}
