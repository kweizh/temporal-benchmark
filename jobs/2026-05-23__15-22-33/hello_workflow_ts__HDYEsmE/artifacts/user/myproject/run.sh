#!/bin/bash
ts-node src/worker.ts &
WORKER_PID=$!
sleep 10
ts-node src/client.ts
CLIENT_RET=$?
kill $WORKER_PID
exit $CLIENT_RET
