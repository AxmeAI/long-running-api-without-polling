"""
Long-running API without polling — Python example.

Submit a report generation intent, observe lifecycle in real time,
receive completion without polling or webhooks.

Usage:
    pip install axme
    export AXME_API_KEY="your-key"
    python main.py
"""

import os
from axme import AxmeClient, AxmeClientConfig


def main():
    client = AxmeClient(
        AxmeClientConfig(api_key=os.environ["AXME_API_KEY"])
    )

    # Submit a long-running operation
    intent_id = client.send_intent(
        {
            "intent_type": "report.generate.v1",
            "to_agent": "agent://myorg/production/report-service",
            "payload": {
                "report_type": "quarterly",
                "format": "pdf",
                "quarter": "Q1-2026",
            },
        }
    )
    print(f"Intent submitted: {intent_id}")

    # Observe lifecycle events in real time (SSE stream, no polling)
    print("Watching lifecycle...")
    for event in client.observe(intent_id):
        status = event.get("status", "")
        print(f"  [{status}] {event.get('event_type', '')}")
        if status in ("COMPLETED", "FAILED", "TIMED_OUT", "CANCELLED"):
            break

    # Fetch final state
    intent = client.get_intent(intent_id)
    print(f"\nFinal status: {intent['intent']['lifecycle_status']}")


if __name__ == "__main__":
    main()
