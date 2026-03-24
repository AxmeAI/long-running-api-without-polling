"""
Report service agent - listens for intents via SSE and processes them.

This agent simulates a report generation service. It receives an intent,
"generates" a report (simulated delay), and resumes with the result.

Usage:
    # Get agent key from scenario-agents.json after running scenario
    export AXME_API_KEY="<agent-key>"
    python agent.py
"""

import os
import sys
import time

# Ensure output is not buffered
sys.stdout.reconfigure(line_buffering=True)

from axme import AxmeClient, AxmeClientConfig


AGENT_ADDRESS = "report-service-demo"


def handle_intent(client, intent_id):
    """Process a single intent - generate report and resume."""
    intent_data = client.get_intent(intent_id)
    intent = intent_data.get("intent", intent_data)
    payload = intent.get("payload", {})
    # Scenario-based intents wrap original payload in parent_payload
    if "parent_payload" in payload:
        payload = payload["parent_payload"]

    report_type = payload.get("report_type", "unknown")
    fmt = payload.get("format", "pdf")
    quarter = payload.get("quarter", "Q1")

    print(f"  Generating {report_type} report ({fmt}) for {quarter}...")
    time.sleep(2)  # Simulate report generation

    result = {
        "action": "complete",
        "report_url": f"https://reports.example.com/{quarter}-{report_type}.{fmt}",
        "pages": 42,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    client.resume_intent(intent_id, result)
    print(f"  Report ready: {result['report_url']}")


def main():
    api_key = os.environ.get("AXME_API_KEY", "")
    if not api_key:
        print("Error: AXME_API_KEY not set.")
        print("Run the scenario first: axme scenarios apply scenario.json")
        print("Then get the agent key from ~/.config/axme/scenario-agents.json")
        sys.exit(1)

    client = AxmeClient(AxmeClientConfig(api_key=api_key))

    print(f"Agent listening on {AGENT_ADDRESS}...")
    print("Waiting for intents (Ctrl+C to stop)\n")

    for delivery in client.listen(AGENT_ADDRESS):
        intent_id = delivery.get("intent_id", "")
        status = delivery.get("status", "")

        if not intent_id:
            continue

        # Process actionable deliveries
        if status in ("DELIVERED", "CREATED", "IN_PROGRESS"):
            print(f"[{status}] Intent received: {intent_id}")
            try:
                handle_intent(client, intent_id)
            except Exception as e:
                print(f"  Error processing intent: {e}")


if __name__ == "__main__":
    main()
