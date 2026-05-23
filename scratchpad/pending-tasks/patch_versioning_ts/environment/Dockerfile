FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio pytest-xprocess && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /workspace && chmod 0777 /workspace

# -----------------------------------------------------------------------------
# Agent project at /home/user/myproject
# -----------------------------------------------------------------------------
RUN mkdir -p /home/user/myproject/src

RUN cat >/home/user/myproject/package.json <<'EOF'
{
  "name": "order-ts",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "ts-node src/worker.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.8",
    "@temporalio/client": "^1.11.8",
    "@temporalio/worker": "^1.11.8",
    "@temporalio/workflow": "^1.11.8"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "ts-node": "^10.9.2",
    "typescript": "^5.3.3"
  }
}
EOF

RUN cat >/home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "outDir": "dist"
  },
  "include": ["src/**/*"]
}
EOF

RUN cat >/home/user/myproject/src/activities.ts <<'EOF'
import * as fs from 'fs';

const ORDER_LOG = '/workspace/order.log';
const NOTIFY_LOG = '/workspace/notify.log';

export async function chargeCard(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  fs.appendFileSync(ORDER_LOG, `charged:${orderId}\n`);
}

export async function shipOrder(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  fs.appendFileSync(ORDER_LOG, `shipped:${orderId}\n`);
}

export async function notifyCustomer(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 500));
  fs.appendFileSync(NOTIFY_LOG, `notified:${orderId}\n`);
}
EOF

# Original (unpatched) workflow: chargeCard -> sleep -> shipOrder
RUN cat >/home/user/myproject/src/workflows.ts <<'EOF'
import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCard, shipOrder, notifyCustomer } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

export async function OrderWorkflow(orderId: string): Promise<void> {
  await chargeCard(orderId);
  await sleep('10 seconds');
  await shipOrder(orderId);
}
EOF

RUN cat >/home/user/myproject/src/worker.ts <<'EOF'
import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function main() {
  const address = process.env.TEMPORAL_ADDRESS;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  if (!address || !apiKey || !namespace) {
    throw new Error('Missing TEMPORAL_ADDRESS / TEMPORAL_API_KEY / TEMPORAL_NAMESPACE');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });

  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: 'order-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  console.log('Worker started');
  await worker.run();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/myproject && npm install --no-audit --no-fund

# -----------------------------------------------------------------------------
# Pre-patch helper at /opt/prepatch:
#   Starts a worker registering the ORIGINAL (unpatched) workflow code and
#   schedules the "old" workflow execution so that its history is recorded
#   without an `add-notify-customer` patch marker. Then the helper exits while
#   the workflow is still mid-execution (during the 10s sleep), so that the
#   agent's worker must replay the started execution and complete it.
# -----------------------------------------------------------------------------
RUN mkdir -p /opt/prepatch/src

RUN cat >/opt/prepatch/package.json <<'EOF'
{
  "name": "prepatch",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@temporalio/activity": "^1.11.8",
    "@temporalio/client": "^1.11.8",
    "@temporalio/worker": "^1.11.8",
    "@temporalio/workflow": "^1.11.8"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "typescript": "^5.3.3"
  }
}
EOF

RUN cat >/opt/prepatch/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["src/**/*"]
}
EOF

RUN cat >/opt/prepatch/src/activities.ts <<'EOF'
import * as fs from 'fs';

const ORDER_LOG = '/workspace/order.log';

export async function chargeCard(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  fs.appendFileSync(ORDER_LOG, `charged:${orderId}\n`);
}

export async function shipOrder(orderId: string): Promise<void> {
  await new Promise((r) => setTimeout(r, 1000));
  fs.appendFileSync(ORDER_LOG, `shipped:${orderId}\n`);
}
EOF

RUN cat >/opt/prepatch/src/workflows.ts <<'EOF'
import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCard, shipOrder } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
});

export async function OrderWorkflow(orderId: string): Promise<void> {
  await chargeCard(orderId);
  await sleep('10 seconds');
  await shipOrder(orderId);
}
EOF

RUN cat >/opt/prepatch/src/start_old.ts <<'EOF'
import { NativeConnection, Worker } from '@temporalio/worker';
import { Connection, Client } from '@temporalio/client';
import * as activities from './activities';

async function main() {
  const address = process.env.TEMPORAL_ADDRESS!;
  const apiKey = process.env.TEMPORAL_API_KEY!;
  const namespace = process.env.TEMPORAL_NAMESPACE!;
  const runId = process.env.ZEALT_RUN_ID!;
  if (!address || !apiKey || !namespace || !runId) {
    throw new Error('Missing required env vars (TEMPORAL_*, ZEALT_RUN_ID)');
  }
  const workflowId = `order-old-${runId}`;

  const workerConnection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });

  const worker = await Worker.create({
    connection: workerConnection,
    namespace,
    taskQueue: 'order-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  const runPromise = worker.run();

  const clientConnection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });
  const client = new Client({ connection: clientConnection, namespace });

  await client.workflow.start('OrderWorkflow', {
    taskQueue: 'order-ts',
    workflowId,
    args: [workflowId],
  });
  console.log(`Started old workflow ${workflowId}`);

  // Give the pre-patch worker enough time to process chargeCard but exit while
  // the workflow is sleeping (sleep is 10 seconds in the workflow definition).
  await new Promise((r) => setTimeout(r, 5000));

  worker.shutdown();
  await runPromise;
  await clientConnection.close();
  await workerConnection.close();
  console.log('Pre-patch worker stopped');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /opt/prepatch && npm install --no-audit --no-fund && \
    ./node_modules/.bin/tsc

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal.io TypeScript SDK environment with an order-processing project that must be modified to safely insert a new activity using versioning-with-patching while a workflow started by a pre-patch worker is mid-execution on Temporal Cloud."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep build-essential
#   - Node.js v20 (NodeSource)
#   - required pip3 packages: pytest-json-ctrf, temporalio, pytest-xprocess
#   - /home/user/myproject: TypeScript Temporal project with unpatched OrderWorkflow that the agent must patch
#   - /opt/prepatch: pre-built helper that starts the "old" workflow on Temporal Cloud
#                   before the agent's worker is launched (used by the verifier)
#   - /workspace: shared directory for order.log and notify.log written by activities
