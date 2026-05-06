FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user/project/src && chmod -R 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal TypeScript project with a non-deterministic workflow bug."

WORKDIR /home/user/project

RUN cat > package.json <<'EOF'
{
  "name": "temporal-project",
  "version": "1.0.0",
  "scripts": {
    "build": "tsc --build",
    "build.watch": "tsc --build --watch",
    "lint": "eslint .",
    "start": "ts-node src/worker.ts",
    "start.watch": "nodemon src/worker.ts",
    "workflow": "ts-node src/client.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.1",
    "@temporalio/client": "^1.11.1",
    "@temporalio/envconfig": "^1.11.1",
    "@temporalio/worker": "^1.11.1",
    "@temporalio/workflow": "^1.11.1"
  },
  "devDependencies": {
    "@tsconfig/node18": "^1.0.0",
    "@types/node": "^18.15.11",
    "nodemon": "^2.0.22",
    "ts-node": "^10.9.1",
    "typescript": "^5.0.4"
  }
}
EOF

RUN cat > tsconfig.json <<'EOF'
{
  "extends": "@tsconfig/node18/tsconfig.json",
  "version": "4.10.0",
  "compilerOptions": {
    "emitDecoratorMetadata": false,
    "experimentalDecorators": false,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true,
    "rootDir": "./src",
    "outDir": "./lib"
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

RUN cat > src/activities.ts <<'EOF'
export async function applyDiscount(amount: number, discount: number): Promise<number> {
  return amount - (amount * discount);
}
EOF

RUN cat > src/workflows.ts <<'EOF'
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { applyDiscount } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

let globalDiscountState = 0.1;

export async function discountWorkflow(amount: number): Promise<number> {
  const currentTime = new Date().getTime();
  
  // A buggy logic relying on system time and global state
  if (currentTime % 2 === 0) {
    globalDiscountState = 0.2;
  } else {
    globalDiscountState = 0.15;
  }
  
  return await applyDiscount(amount, globalDiscountState);
}
EOF

RUN cat > src/worker.ts <<'EOF'
import { Worker } from '@temporalio/worker';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import * as activities from './activities';

async function run() {
  const config = loadClientConnectConfig();
  
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflows'),
    activities,
    taskQueue: 'discount-task-queue',
    connectionOptions: config.connectionOptions,
    namespace: config.namespace,
  });

  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cat > src/client.ts <<'EOF'
import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import { discountWorkflow } from './workflows';

async function run() {
  const config = loadClientConnectConfig();
  const connection = await Connection.connect(config.connectionOptions);
  
  const client = new Client({
    connection,
    namespace: config.namespace,
  });

  const handle = await client.workflow.start(discountWorkflow, {
    taskQueue: 'discount-task-queue',
    workflowId: 'discount-wf-' + Date.now(),
    args: [100],
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

RUN npm install

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
