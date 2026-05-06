FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Node.js project with Temporal SDK installed."

RUN mkdir -p /home/user/temporal-app && \
    cd /home/user/temporal-app && \
    npm init -y && \
    npm install @temporalio/client @temporalio/worker @temporalio/workflow @temporalio/activity @temporalio/envconfig axios && \
    npm install -D typescript ts-node @tsconfig/node20 && \
    cat >tsconfig.json <<'EOF'
{
  "extends": "@tsconfig/node20/tsconfig.json",
  "compilerOptions": {
    "outDir": "./lib",
    "rootDir": "./src",
    "module": "commonjs",
    "target": "es2022"
  },
  "include": ["src/**/*"]
}
EOF
RUN mkdir -p /home/user/temporal-app/src

# Container contents:
#   - Node.js v24 installed
#   - /home/user/temporal-app - Initialized Node.js project with Temporal SDK dependencies, axios, ts-node, and typescript.
#   - tsconfig.json configured for Temporal.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
