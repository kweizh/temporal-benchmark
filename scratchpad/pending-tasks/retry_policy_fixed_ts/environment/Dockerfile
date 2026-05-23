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
RUN mkdir -p /workspace && chmod 0755 /workspace

# --- Scaffold the TypeScript Temporal project skeleton at /home/user/myproject ---
RUN mkdir -p /home/user/myproject/src

RUN cat >/home/user/myproject/package.json <<'EOF'
{
  "name": "temporal-retry-policy-fixed-ts",
  "version": "1.0.0",
  "private": true,
  "description": "Temporal TypeScript project skeleton: implement a flaky activity with a fixed-interval Activity RetryPolicy.",
  "scripts": {
    "worker": "ts-node src/worker.ts",
    "client": "ts-node src/client.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.7",
    "@temporalio/client": "^1.11.7",
    "@temporalio/common": "^1.11.7",
    "@temporalio/worker": "^1.11.7",
    "@temporalio/workflow": "^1.11.7"
  },
  "devDependencies": {
    "@types/node": "^20.11.30",
    "ts-node": "^10.9.2",
    "typescript": "^5.4.5"
  }
}
EOF

RUN cat >/home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": false,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "outDir": "dist",
    "rootDir": "src",
    "lib": ["ES2020", "DOM"]
  },
  "include": ["src/**/*.ts"]
}
EOF

RUN cat >/home/user/myproject/src/worker.ts <<'EOF'
import { NativeConnection, Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  if (!address || !namespace || !apiKey) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set.');
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
    taskQueue: 'retry-ts',
    workflowsPath: require.resolve('./workflows'),
    activities,
  });

  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cat >/home/user/myproject/src/client.ts <<'EOF'
import * as fs from 'fs';
import * as path from 'path';
import { Connection, Client } from '@temporalio/client';

async function run(): Promise<void> {
  const address = process.env.TEMPORAL_ADDRESS;
  const namespace = process.env.TEMPORAL_NAMESPACE;
  const apiKey = process.env.TEMPORAL_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;
  if (!address || !namespace || !apiKey || !runId) {
    throw new Error('TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY, and ZEALT_RUN_ID must be set.');
  }

  const connection = await Connection.connect({
    address,
    tls: true,
    apiKey,
    metadata: { 'temporal-namespace': namespace },
  });
  const client = new Client({ connection, namespace });

  const workflowId = `retry-${runId}`;
  const result: string = await client.workflow.execute('FlakyWorkflow', {
    taskQueue: 'retry-ts',
    workflowId,
    args: [],
  });

  const line = `Workflow result: ${result}\n`;
  console.log(line.trimEnd());
  const logPath = path.join('/home/user/myproject', 'output.log');
  fs.appendFileSync(logPath, line);

  await connection.close();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

# Install npm dependencies so node_modules is populated at start time.
RUN cd /home/user/myproject && npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="Temporal TypeScript SDK task: implement a flaky activity with a fixed-interval Activity RetryPolicy that retries 5 times with 2s delay."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - pip3 packages for verification: temporalio (Python SDK)
#   - Node.js v24 + npm
#   - /workspace: scratch directory used by the flaky activity to record attempts (/workspace/attempts.log)
#   - /home/user/myproject: TypeScript Temporal project skeleton (package.json, tsconfig.json, src/worker.ts, src/client.ts)
#   - /home/user/myproject/node_modules: preinstalled @temporalio/* + ts-node + typescript
