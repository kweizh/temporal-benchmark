"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.finishSignal = exports.incrementSignal = void 0;
exports.CounterWorkflow = CounterWorkflow;
const workflow_1 = require("@temporalio/workflow");
// Define signals
exports.incrementSignal = (0, workflow_1.defineSignal)('increment');
exports.finishSignal = (0, workflow_1.defineSignal)('finish');
async function CounterWorkflow() {
    let counter = 0;
    let done = false;
    // Handle increment signal: add the given value to the counter
    (0, workflow_1.setHandler)(exports.incrementSignal, (value) => {
        counter += value;
    });
    // Handle finish signal: set the done flag
    (0, workflow_1.setHandler)(exports.finishSignal, () => {
        done = true;
    });
    // Block until the finish signal sets done = true
    await (0, workflow_1.condition)(() => done);
    return counter;
}
