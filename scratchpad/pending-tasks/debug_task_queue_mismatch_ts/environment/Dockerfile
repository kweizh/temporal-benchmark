FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash wget jq && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    mv ~/.temporalio/bin/temporal /usr/local/bin/temporal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal TypeScript project with a Task Queue mismatch bug."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    npm init -y && \
    npm install @temporalio/client @temporalio/worker @temporalio/workflow @temporalio/activity typescript @tsconfig/node16 @types/node && \
    mkdir -p src && \
    cat > tsconfig.json <<'EOF'
{
  "extends": "@tsconfig/node16/tsconfig.json",
  "version": "4.1.2",
  "compilerOptions": {
    "outDir": "./lib",
    "rootDir": "./src"
  }
}
EOF

RUN cd /home/user/project && \
    cat > src/workflows.ts <<'EOF'
import { proxyActivities } from '@temporalio/workflow';

export async function MyWorkflow(): Promise<string> {
  return 'Hello, Temporal!';
}
EOF

RUN cd /home/user/project && \
    cat > src/client.ts <<'EOF'
import { Connection, Client } from '@temporalio/client';

async function run() {
  const connection = await Connection.connect({ address: 'localhost:7233' });
  const client = new Client({ connection });

  const handle = await client.workflow.start('MyWorkflow', {
    taskQueue: 'my-task-queue',
    workflowId: 'my-workflow-id-' + Math.floor(Math.random() * 1000),
  });
  console.log(`Started workflow ${handle.workflowId}`);

  const result = await handle.result();
  console.log(result);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/project && \
    cat > src/worker.ts <<'EOF'
import { Worker } from '@temporalio/worker';
import * as workflows from './workflows';

async function run() {
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflows'),
    taskQueue: 'wrong-task-queue',
  });
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/project && \
    cat > package.json <<'EOF'
{
  "name": "project",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "build": "tsc"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.2",
    "@temporalio/client": "^1.11.2",
    "@temporalio/worker": "^1.11.2",
    "@temporalio/workflow": "^1.11.2"
  },
  "devDependencies": {
    "@tsconfig/node16": "^16.1.3",
    "@types/node": "^16.18.96",
    "typescript": "^5.4.5"
  }
}
EOF

# Container contents:
#   - Node.js v20 and Temporal CLI installed.
#   - /home/user/project: A Temporal TypeScript project with a Task Queue mismatch bug.

# Start temporal server in background and keep container alive
CMD ["/bin/bash", "-c", "temporal server start-dev & trap : TERM INT; sleep infinity & wait"]