FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep \
        build-essential && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf temporalio==1.18.1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Create the broken Temporal TypeScript project that the agent will fix.
RUN mkdir -p /home/user/myproject/src

RUN cat > /home/user/myproject/package.json <<'EOF'
{
  "name": "discount-workflow",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "worker": "ts-node src/worker.ts",
    "client": "ts-node src/client.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.8",
    "@temporalio/client": "^1.11.8",
    "@temporalio/worker": "^1.11.8",
    "@temporalio/workflow": "^1.11.8"
  },
  "devDependencies": {
    "@types/node": "^20.12.7",
    "ts-node": "^10.9.2",
    "typescript": "^5.4.5"
  }
}
EOF

RUN cat > /home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "outDir": "lib",
    "rootDir": "src",
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}
EOF

# BROKEN initial Workflow file: uses Math.random and `new Date(` directly.
RUN cat > /home/user/myproject/src/workflows.ts <<'EOF'
// DiscountWorkflow picks a percentage discount for a user.
//
// NOTE: This implementation is intentionally broken. It violates Temporal's
// deterministic execution constraints by reading the wall-clock time and
// generating random numbers directly inside the Workflow body.
//
// Your task is to refactor this Workflow so that:
//   * The current time is obtained through a Temporal Workflow-safe API
//     (e.g. `workflow.now()`), not via `new Date(...)`.
//   * Random discount selection is delegated to an Activity named
//     `pickDiscount` declared in `./activities`, which the Workflow invokes
//     through `proxyActivities`.

export interface DiscountResult {
  userId: string;
  discount: number;
  decidedAt: number;
}

export async function DiscountWorkflow(userId: string): Promise<DiscountResult> {
  const options = [0, 5, 10, 15, 20];
  // BROKEN: Non-deterministic random call inside the Workflow body.
  const idx = Math.floor(Math.random() * options.length);
  const discount = options[idx];
  // BROKEN: Direct wall-clock read inside the Workflow body.
  const decidedAt = new Date().getTime();
  return { userId, discount, decidedAt };
}
EOF

# Empty-ish activities file. Agent must add `pickDiscount`.
RUN cat > /home/user/myproject/src/activities.ts <<'EOF'
// Define Temporal Activity functions here.
//
// The Workflow in `./workflows.ts` is expected to call an Activity called
// `pickDiscount()` that returns one of [0, 5, 10, 15, 20] chosen at random.
//
// Activities may freely use non-deterministic APIs such as `Math.random`,
// `Date`, network calls, and database access.

export async function healthCheck(): Promise<string> {
  return 'ok';
}
EOF

RUN cat > /home/user/myproject/src/worker.ts <<'EOF'
import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  if (!address || !namespace || !apiKey) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set');
  }

  const connection = await NativeConnection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });

  try {
    const worker = await Worker.create({
      connection,
      namespace,
      taskQueue: 'discount-ts',
      workflowsPath: require.resolve('./workflows'),
      activities,
    });
    await worker.run();
  } finally {
    await connection.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cat > /home/user/myproject/src/client.ts <<'EOF'
import * as fs from 'fs';
import * as path from 'path';
import { Connection, Client } from '@temporalio/client';
import { DiscountWorkflow, DiscountResult } from './workflows';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;
  if (!address || !namespace || !apiKey) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set');
  }
  if (!runId) {
    throw new Error('ZEALT_RUN_ID must be set');
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });

  try {
    const client = new Client({ connection, namespace });
    const workflowId = `discount-${runId}`;
    const handle = await client.workflow.start(DiscountWorkflow, {
      args: ['user-42'],
      taskQueue: 'discount-ts',
      workflowId,
    });
    console.log(`Started workflow ${handle.workflowId}`);
    const result: DiscountResult = await handle.result();
    console.log('Workflow result:', JSON.stringify(result));
    const logFile = path.resolve(__dirname, '..', 'output.log');
    fs.appendFileSync(logFile, `Discount: ${result.discount}\n`);
  } finally {
    await connection.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

# Install npm dependencies eagerly so the executor doesn't have to pay the
# cost of a cold install and so subsequent `npm run worker/client` invocations
# are fast.
RUN cd /home/user/myproject && npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="Broken Temporal TypeScript Workflow project for the fix_nondeterministic_workflow_ts task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 + npm via NodeSource for the Temporal TypeScript SDK runtime
#   - temporalio Python SDK (for the verifier)
#   - /home/user/myproject: Temporal TS project (package.json, tsconfig.json, src/{workflows,activities,worker,client}.ts) with node_modules pre-installed
#   - /home/user/myproject/src/workflows.ts: INTENTIONALLY BROKEN (uses Math.random and new Date())
