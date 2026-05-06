import os
import subprocess
import time
import json
import pytest

PROJECT_DIR = "/home/user/money-transfer"

@pytest.fixture(scope="module")
def start_worker():
    # Start the worker
    process = subprocess.Popen(
        ["npm", "run", "worker"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the worker to be ready
    time.sleep(10)

    yield

    # Shut down the worker
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_saga_failure_and_success_scenarios(start_worker):
    # We create a small TS script to verify the behavior
    # using the user's installed @temporalio/client
    verifier_script = os.path.join(PROJECT_DIR, "verifier.ts")
    with open(verifier_script, "w") as f:
        f.write("""
import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';

async function run() {
  const config = loadClientConnectConfig();
  const connection = await Connection.connect(config.connectionOptions);
  const client = new Client({
    connection,
    namespace: config.namespace
  });

  // Test 1: Failing scenario
  const failWfId = 'saga-fail-' + Date.now();
  const failHandle = await client.workflow.start('moneyTransferSaga', {
    taskQueue: 'money-transfer-queue',
    workflowId: failWfId,
    args: ['accA', 'fail', 100]
  });

  try {
    await failHandle.result();
  } catch (e) {
    // Expected to fail or complete after compensation
  }

  // Fetch history for failWfId
  const failHistory = await client.workflowService.getWorkflowExecutionHistory({
    namespace: config.namespace,
    execution: { workflowId: failWfId }
  });

  const failActivities = failHistory.history.events
    .filter(e => e.activityTaskScheduledEventAttributes)
    .map(e => e.activityTaskScheduledEventAttributes.activityType.name);

  if (!failActivities.includes('withdraw') || !failActivities.includes('deposit') || !failActivities.includes('refund')) {
    console.error('FAIL_SCENARIO_MISSING_ACTIVITIES', failActivities);
    process.exit(1);
  }

  // Test 2: Success scenario
  const successWfId = 'saga-success-' + Date.now();
  const successHandle = await client.workflow.start('moneyTransferSaga', {
    taskQueue: 'money-transfer-queue',
    workflowId: successWfId,
    args: ['accA', 'accB', 100]
  });

  await successHandle.result();

  // Fetch history for successWfId
  const successHistory = await client.workflowService.getWorkflowExecutionHistory({
    namespace: config.namespace,
    execution: { workflowId: successWfId }
  });

  const successActivities = successHistory.history.events
    .filter(e => e.activityTaskScheduledEventAttributes)
    .map(e => e.activityTaskScheduledEventAttributes.activityType.name);

  if (!successActivities.includes('withdraw') || !successActivities.includes('deposit')) {
    console.error('SUCCESS_SCENARIO_MISSING_ACTIVITIES', successActivities);
    process.exit(1);
  }

  if (successActivities.includes('refund')) {
    console.error('SUCCESS_SCENARIO_UNEXPECTED_REFUND', successActivities);
    process.exit(1);
  }

  console.log('ALL_PASSED');
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
""")

    # Run the verifier script using ts-node or npx tsx
    # Since we don't know if the user installed ts-node globally, we can use npx tsx which downloads if needed
    result = subprocess.run(
        ["npx", "tsx", "verifier.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Verifier script failed: {result.stderr}\\n{result.stdout}"
    assert "ALL_PASSED" in result.stdout, f"Verifier output did not indicate success: {result.stdout}\\n{result.stderr}"
