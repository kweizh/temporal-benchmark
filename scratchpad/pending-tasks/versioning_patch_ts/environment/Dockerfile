FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal TypeScript project with initial workflow."

RUN mkdir -p /home/user/project/src && \
    cd /home/user/project && \
    cat > package.json <<'EOF'
{
  "name": "temporal-project",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc --build",
    "start": "ts-node src/worker.ts",
    "workflow": "ts-node src/client.ts"
  },
  "dependencies": {
    "@temporalio/client": "^1.11.0",
    "@temporalio/worker": "^1.11.0",
    "@temporalio/workflow": "^1.11.0",
    "@temporalio/activity": "^1.11.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "ts-node": "^10.9.1"
  }
}
EOF

RUN cd /home/user/project && \
    cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "CommonJS",
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src"]
}
EOF

RUN cd /home/user/project && \
    cat > src/activities.ts <<'EOF'
export async function chargeCustomer(orderId: string): Promise<string> {
  return `charged v1 ${orderId}`;
}
export async function chargeCustomerV2(orderId: string): Promise<string> {
  return `charged v2 ${orderId}`;
}
EOF

RUN cd /home/user/project && \
    cat > src/workflows.ts <<'EOF'
import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { chargeCustomer, chargeCustomerV2 } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function processOrder(orderId: string): Promise<string> {
  await sleep('100 milliseconds');
  await chargeCustomer(orderId);
  return 'processed';
}
EOF

RUN cd /home/user/project && \
    cat > src/worker.ts <<'EOF'
import { Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflows'),
    activities,
    taskQueue: 'tutorial',
  });
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/project && \
    cat > src/client.ts <<'EOF'
import { Connection, Client } from '@temporalio/client';
import { processOrder } from './workflows';

async function run() {
  const connection = await Connection.connect();
  const client = new Client({ connection });

  const handle = await client.workflow.start(processOrder, {
    args: ['order-123'],
    taskQueue: 'tutorial',
    workflowId: 'workflow-' + Math.random(),
  });
  console.log(`Started workflow ${handle.workflowId}`);
  const result = await handle.result();
  console.log(`Result: ${result}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/project && npm install

# Container contents:
#   - Node.js and Temporal CLI installed.
#   - /home/user/project: A Temporal TypeScript project with package.json, activities, workflows, worker, client.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
