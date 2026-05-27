#!/bin/bash
npx ts-node src/worker.ts &
WORKER_PID=$!
sleep 10
npx ts-node src/client.ts
kill $WORKER_PID
