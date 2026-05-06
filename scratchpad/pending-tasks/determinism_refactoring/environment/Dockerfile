FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSf https://temporal.download/cli.sh | sh && \
    cp /root/.temporalio/bin/temporal /usr/local/bin/temporal

RUN pip3 install --break-system-packages temporalio requests pytest pytest-asyncio

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Temporal Python SDK task environment for fixing determinism issues."

RUN mkdir -p /home/user/temporal-determinism && \
    cd /home/user/temporal-determinism && \
    cat > requirements.txt <<'EOF'
temporalio
requests
pytest
pytest-asyncio
EOF

RUN cd /home/user/temporal-determinism && \
    cat > workflow.py <<'EOF'
from temporalio import workflow
import datetime
import uuid
import requests
from datetime import timedelta
import asyncio

@workflow.defn
class ReportWorkflow:
    @workflow.run
    async def run(self) -> dict:
        # Non-deterministic calls
        current_time = datetime.datetime.now().isoformat()
        report_id = str(uuid.uuid4())
        
        # Blocking network IO directly in workflow
        response = requests.get("http://localhost:8080/data")
        data = response.json()
        
        return {
            "report_id": report_id,
            "generated_at": current_time,
            "data": data.get("result", "no data")
        }
EOF

RUN cd /home/user/temporal-determinism && \
    cat > activity.py <<'EOF'
from temporalio import activity

# Empty activity file, agent needs to create fetch_data here
EOF

RUN cd /home/user/temporal-determinism && \
    cat > worker.py <<'EOF'
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import ReportWorkflow
import activity

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="determinism-task-queue",
        workflows=[ReportWorkflow],
        activities=[], # Agent needs to add fetch_data here
    )
    print("Starting worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cd /home/user/temporal-determinism && \
    cat > run_workflow.py <<'EOF'
import asyncio
from temporalio.client import Client
from workflow import ReportWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        ReportWorkflow.run,
        id="report-workflow-id",
        task_queue="determinism-task-queue",
    )
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

RUN cd /home/user/temporal-determinism && \
    cat > server.py <<'EOF'
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"result": "success data"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=MockServerRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting mock server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
EOF

# Container contents:
#   - temporal cli
#   - python3, pip, temporalio, requests
#   - /home/user/temporal-determinism with broken workflow files

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
