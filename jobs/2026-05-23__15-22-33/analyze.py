import os
import json
import re

TASKS_DIR = "/home/kw/code/zealt/temporal-benchmark/tasks"
RESULTS_FILE = "result.json"

def main():
    with open(RESULTS_FILE) as f:
        results = json.load(f)
    
    rewards = results["stats"]["evals"]["pochi__gemini-3-flash__tasks"]["reward_stats"]["reward"]
    passed = [x.split("__")[0] for x in rewards.get("1.0", [])]
    failed = [x.split("__")[0] for x in rewards.get("0.0", [])]
    
    print("| Task | Flash Result | Research Plan Changes | Skill Changes | Minor Fix | Discard |")
    print("|---|---|---|---|---|---|")
    
    for task in passed + failed:
        status = "✅Pass" if task in passed else "❌Fail"
        
        task_dir = os.path.join(TASKS_DIR, task)
        test_file = os.path.join(task_dir, "tests", "test_final_state.py")
        
        test_content = ""
        if os.path.exists(test_file):
            with open(test_file) as f:
                test_content = f.read()
                
        # Simple heuristic to see if test actually runs something or just checks file content
        if "subprocess.run" not in test_content and "temporalio" not in test_content and "Worker" not in test_content and "Client" not in test_content:
            issue = "Only checking file content, not running worker/client"
        else:
            issue = ""
            
        print(f"| {task} | {status} | | {issue} | | |")

if __name__ == '__main__':
    main()
