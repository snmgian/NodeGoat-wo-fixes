from urllib import request
import json
import os
import uuid

DEFAULT_LANGGRAPH_SERVER_URL = 'http://127.0.0.1:2024'

def build_test_issue():
    return { "issue_id": 0, "issue_title": "OWASP Test Issue", "issue_body": "OWASP Test Issue Body"}

def extract_issue(event_context):
    issue_id = event_context["issue"]["id"]
    issue_title = event_context["issue"]["title"]
    issue_body = event_context["issue"]["body"]

    return {
        "issue_id": issue_id,
        "issue_title": issue_title,
        "issue_body": issue_body,
    }

def get_langgraph_server_url(event_context, repository_vars):
    issue_user_login = event_context["issue"]["user"]["login"]
    langgraph_server_url_var = f"LANGGRAPH_SERVER_URL_{issue_user_login.upper()}"
    return repository_vars.get(langgraph_server_url_var, DEFAULT_LANGGRAPH_SERVER_URL)

def make_request(issue_data, langgraph_server_url):
    thread_id = str(uuid.uuid4())
    url = f"{langgraph_server_url}/threads/{thread_id}/runs"

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

    response = request.urlopen(req, data=data)
    content = response.read()
    print(content)

def main():
    event_context = json.loads(os.environ.get('EVENT_CONTEXT', "{}"))
    repository_vars = json.loads(os.environ.get('REPOSITORY_VARS', "{}"))

    if event_context:
        issue_data = extract_issue(event_context)
    else:
        issue_data = build_test_issue()

    langgraph_server_url = get_langgraph_server_url(event_context, repository_vars)

    make_request(issue_data, langgraph_server_url)

if __name__ == "__main__":
    main()
