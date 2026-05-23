FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/myproject /home/user/myproject/src
RUN mkdir -p /workspace && chmod 0777 /workspace

# Starter package.json with the official Temporal TypeScript SDK packages.
RUN cat >/home/user/myproject/package.json <<'EOF'
{
  "name": "loop-ts",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "ts-node src/main.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.1",
    "@temporalio/client": "^1.11.1",
    "@temporalio/worker": "^1.11.1",
    "@temporalio/workflow": "^1.11.1"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "ts-node": "^10.9.2",
    "typescript": "^5.4.0"
  }
}
EOF

# Minimal tsconfig.json suitable for the Temporal TS SDK.
RUN cat >/home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "moduleResolution": "node",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "outDir": "lib"
  },
  "include": ["src/**/*.ts"]
}
EOF

# Activity file: incrementCounter is already implemented correctly.
RUN cat >/home/user/myproject/src/activities.ts <<'EOF'
import * as fs from 'fs';
import * as path from 'path';

const LOG_PATH = '/workspace/loop.log';

export async function incrementCounter(currentValue: number): Promise<number> {
  const next = currentValue + 1;
  fs.mkdirSync(path.dirname(LOG_PATH), { recursive: true });
  fs.appendFileSync(LOG_PATH, `${next}\n`);
  return next;
}
EOF

# Workflow file: BROKEN naive implementation. The agent must refactor this
# to use `continueAsNew` every 10 iterations.
RUN cat >/home/user/myproject/src/workflows.ts <<'EOF'
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { incrementCounter } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

/**
 * BROKEN: This implementation loops from `start` to `target` in a single
 * Run Id. For long loops this accumulates a huge event history and risks
 * hitting Temporal's history limits. Refactor it to call `continueAsNew`
 * every 10 iterations, passing the current counter value forward as the
 * new `start` argument.
 */
export async function LongLoopWorkflow(start: number, target: number): Promise<number> {
  let counter = start;
  while (counter < target) {
    counter = await incrementCounter(counter);
  }
  return counter;
}
EOF

# Worker entrypoint.
RUN cat >/home/user/myproject/src/worker.ts <<'EOF'
import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

export async function runWorker(): Promise<Worker> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  if (!address || !namespace || !apiKey) {
    throw new Error(
      'TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set',
    );
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'loop-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  return worker;
}
EOF

# Client entrypoint.
RUN cat >/home/user/myproject/src/client.ts <<'EOF'
import { Connection, Client } from '@temporalio/client';
import { LongLoopWorkflow } from './workflows';

export async function runClient(): Promise<number> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;
  if (!address || !namespace || !apiKey || !runId) {
    throw new Error(
      'TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY, and ZEALT_RUN_ID must be set',
    );
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
  });

  const client = new Client({ connection, namespace });

  const handle = await client.workflow.start(LongLoopWorkflow, {
    args: [0, 25],
    taskQueue: 'loop-ts',
    workflowId: `loop-${runId}`,
  });

  const result = await handle.result();
  console.log(`Final result: ${result}`);
  return result;
}
EOF

# Main entrypoint: launches the worker and the client.
RUN cat >/home/user/myproject/src/main.ts <<'EOF'
import { runWorker } from './worker';
import { runClient } from './client';

async function main(): Promise<void> {
  const worker = await runWorker();
  const workerRun = worker.run();
  try {
    await runClient();
  } finally {
    worker.shutdown();
    await workerRun;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

# Pre-install npm dependencies so the agent does not have to spend time on
# network installs at runtime.
RUN cd /home/user/myproject && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io TypeScript SDK task environment with Node.js v24 and the Python temporalio SDK for verifying a LongLoopWorkflow that must be refactored to use continueAsNew, including a /workspace directory for the incrementCounter activity log."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for the Temporal TypeScript SDK task environment
#   - temporalio Python SDK installed via pip3 for verifying workflow execution in Temporal Cloud
#   - /home/user/myproject: starter Temporal TS project (broken LongLoopWorkflow that loops without continueAsNew)
#   - /workspace: writable directory where the incrementCounter activity appends to loop.log
