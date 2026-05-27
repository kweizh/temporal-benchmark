"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.finishSignal = exports.incrementSignal = void 0;
exports.CounterWorkflow = CounterWorkflow;
const workflow_1 = require("@temporalio/workflow");
exports.incrementSignal = (0, workflow_1.defineSignal)('increment');
exports.finishSignal = (0, workflow_1.defineSignal)('finish');
async function CounterWorkflow() {
    let counter = 0;
    let isDone = false;
    (0, workflow_1.setHandler)(exports.incrementSignal, (amount) => {
        counter += amount;
    });
    (0, workflow_1.setHandler)(exports.finishSignal, () => {
        isDone = true;
    });
    await (0, workflow_1.condition)(() => isDone);
    return counter;
}
