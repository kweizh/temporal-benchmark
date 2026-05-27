"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FetchUrlWorkflow = FetchUrlWorkflow;
const workflow_1 = require("@temporalio/workflow");
const { fetchData } = (0, workflow_1.proxyActivities)({
    startToCloseTimeout: '30 seconds',
});
async function FetchUrlWorkflow(url) {
    return await fetchData(url);
}
