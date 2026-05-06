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
LABEL Description="Temporal TypeScript project with a failing activity that needs a custom retry policy."

RUN mkdir -p /home/user/temporal-project/src && \
    cd /home/user/temporal-project && \
    cat >package.json <<'EOF'
{
  "name": "temporal-project",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "tsc --build",
    "build.watch": "tsc --build --watch",
    "lint": "eslint .",
    "start": "ts-node src/worker.ts",
    "start.watch": "nodemon src/worker.ts",
    "start.client": "ts-node src/client.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.2",
    "@temporalio/client": "^1.11.2",
    "@temporalio/worker": "^1.11.2",
    "@temporalio/workflow": "^1.11.2"
  },
  "devDependencies": {
    "@tsconfig/node18": "^18.2.2",
    "@types/node": "^20.10.0",
    "nodemon": "^3.0.2",
    "ts-node": "^10.9.1",
    "typescript": "^5.3.2"
  }
}
EOF

RUN cd /home/user/temporal-project && \
    cat >tsconfig.json <<'EOF'
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
    "outDir": "./lib",
    "lib": ["esnext"],
    "strict": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

RUN cd /home/user/temporal-project && \
    cat >src/activities.ts <<'EOF'
export async function alwaysFailActivity(): Promise<string> {
  throw new Error("This activity always fails.");
}
EOF

RUN cd /home/user/temporal-project && \
    cat >src/workflows.ts <<'EOF'
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { alwaysFailActivity } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function exampleWorkflow(): Promise<string> {
  return await alwaysFailActivity();
}
EOF

RUN cd /home/user/temporal-project && \
    cat >src/worker.ts <<'EOF'
import { Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflows'),
    activities,
    taskQueue: 'retry-task-queue',
  });
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/temporal-project && \
    cat >src/client.ts <<'EOF'
import { Connection, Client } from '@temporalio/client';
import { exampleWorkflow } from './workflows';

async function run() {
  const connection = await Connection.connect({ address: 'localhost:7233' });
  const client = new Client({ connection });

  try {
    const handle = await client.workflow.start(exampleWorkflow, {
      taskQueue: 'retry-task-queue',
      workflowId: 'retry-workflow-id',
    });
    console.log(`Started workflow ${handle.workflowId}`);
    
    // Wait for result, it should throw
    await handle.result();
  } catch (err) {
    console.log("Workflow failed as expected.");
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

# Install dependencies so the environment is ready
RUN cd /home/user/temporal-project && npm install

# Container contents:
#   - Node.js v24 and Temporal CLI installed.
#   - /home/user/temporal-project - Initialized Temporal TypeScript project with a failing activity.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]