from urllib import request
import json
import os
import uuid

# LANGGRAPH_SERVER_URL = 'http://127.0.0.1:2024'
LANGGRAPH_SERVER_URL = 'https://2830-2a09-bac0-1000-307-00-2c-da.ngrok-free.app'

def build_test_issue():
    return { "issue_id": 0, "issue_title": "OWASP Test Issue", "issue_body": "OWASP Test Issue Body"}

def extract_issue(event_context):
    data = json.loads(event_context)
    from pprint import pprint
    pprint(data)
    issue_id = data["issue"]["id"]
    issue_title = data["issue"]["title"]
    issue_body = data["issue"]["body"]

    return {
        "issue_id": issue_id,
        "issue_title": issue_title,
        "issue_body": issue_body,
    }

def make_request(issue_data):
    thread_id = str(uuid.uuid4())
    url = f"{LANGGRAPH_SERVER_URL}/threads/{thread_id}/runs"

    req = request.Request(url, method="POST")
    req.add_header('Content-Type', 'application/json')

    input_payload = {
        "messages":[
            {
                "content": "github-issue-created",
                "role": "tool",
                "tool_call_id": "github",
                "artifact": {
                    "issue_id": issue_data["issue_id"],
                    "issue_title": issue_data["issue_title"],
                    "issue_body": issue_data["issue_body"],
                }
            }
        ]
    }

    langgraph_payload = {
        "input": input_payload,
        "assistant_id": "agent",
        "if_not_exists": "create",
    }

    data = json.dumps(langgraph_payload)
    data = data.encode()

    r = request.urlopen(req, data=data)
    content = r.read()
    print(content)


event_context = os.environ.get('EVENT_CONTEXT', None)
if event_context:
    issue_data = extract_issue(event_context)
else:
    issue_data = build_test_issue()

make_request(issue_data)


