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
LABEL Description="Temporal TypeScript project for refactoring a long-running loop to use continueAsNew."

RUN mkdir -p /home/user/project/src && \
    cd /home/user/project && \
    npm init -y && \
    npm install @temporalio/client @temporalio/worker @temporalio/workflow @temporalio/activity @temporalio/envconfig typescript @tsconfig/node20 && \
    npm install --save-dev ts-node

RUN cd /home/user/project && \
    cat >tsconfig.json <<'EOF'
{
  "extends": "@tsconfig/node20/tsconfig.json",
  "compilerOptions": {
    "outDir": "./lib",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
EOF

RUN cd /home/user/project && \
    cat >package.json <<'EOF'
{
  "name": "project",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "build": "tsc",
    "start.worker": "ts-node src/worker.ts",
    "start.client": "ts-node src/client.ts"
  },
  "dependencies": {
    "@temporalio/activity": "^1.11.0",
    "@temporalio/client": "^1.11.0",
    "@temporalio/worker": "^1.11.0",
    "@temporalio/workflow": "^1.11.0",
    "@temporalio/envconfig": "^1.11.0"
  },
  "devDependencies": {
    "@tsconfig/node20": "^20.1.4",
    "ts-node": "^10.9.2",
    "typescript": "^5.5.3"
  }
}
EOF

RUN cd /home/user/project && \
    cat >src/workflows.ts <<'EOF'
import { sleep } from '@temporalio/workflow';

export async function processItemsWorkflow(startIndex: number = 0): Promise<number> {
  let processed = startIndex;
  for (let i = startIndex; i < 1000; i++) {
    // simulate work
    await sleep(1);
    processed++;
  }
  return processed;
}
EOF

RUN cd /home/user/project && \
    cat >src/worker.ts <<'EOF'
import { Worker, NativeConnection } from '@temporalio/worker';
import { loadClientConnectConfig } from '@temporalio/envconfig';

async function run() {
  const config = loadClientConnectConfig();
  const connection = await NativeConnection.connect(config.connectionOptions);
  
  const worker = await Worker.create({
    connection,
    namespace: config.namespace,
    workflowsPath: require.resolve('./workflows'),
    taskQueue: 'continue-as-new-queue',
  });
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

RUN cd /home/user/project && \
    cat >src/client.ts <<'EOF'
import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import * as fs from 'fs';

async function run() {
  const config = loadClientConnectConfig();
  const connection = await Connection.connect(config.connectionOptions);
  
  const client = new Client({
    connection,
    namespace: config.namespace,
  });

  const workflowId = 'process-items-workflow-' + Date.now();
  const handle = await client.workflow.start('processItemsWorkflow', {
    taskQueue: 'continue-as-new-queue',
    workflowId,
    args: [0],
  });

  console.log(`Started workflow ${handle.workflowId}`);
  fs.writeFileSync('workflow_id.txt', handle.workflowId);
  
  const result = await handle.result();
  console.log(`Result: ${result}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
EOF

# Container contents:
#   - Node.js v24, Temporal CLI
#   - /home/user/project: Temporal TS project with workflows.ts, worker.ts, client.ts
#   - Initial workflow processes 1000 items in a single loop without continueAsNew.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
