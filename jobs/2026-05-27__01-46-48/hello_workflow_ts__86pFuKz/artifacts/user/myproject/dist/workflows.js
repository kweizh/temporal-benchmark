"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HelloWorkflow = HelloWorkflow;
const workflow_1 = require("@temporalio/workflow");
const { greet } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '10 seconds',
});
async function HelloWorkflow(name) {
    return await greet(name);
}
//# sourceMappingURL=workflows.js.map