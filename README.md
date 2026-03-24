# Long-Running API Without Polling

Your API call takes 5 minutes. Your client polls every 2 seconds. Your server tracks job state in Redis. Your webhook retries fail silently. Your users see spinners.

**There is a better way.** Submit an intent, walk away, get notified when it completes — with built-in retries, timeouts, and human approval gates.

> **Alpha** · Built with [AXME](https://github.com/AxmeAI/axme) (AXP Intent Protocol).
> [cloud.axme.ai](https://cloud.axme.ai) · [hello@axme.ai](mailto:hello@axme.ai)

---

## The Problem

Every team building async APIs reinvents the same broken stack:

```
Client → POST /reports/generate → 202 Accepted + job_id
Client → GET /reports/status/job_id  (poll every 2s... 50 times)
Client → GET /reports/status/job_id  → 200 { "status": "done", "url": "..." }
```

What breaks:
- **Polling wastes resources** — 50 requests to learn one thing
- **Webhooks fail silently** — retry logic, signatures, dead letters
- **State tracking is DIY** — Redis/DB job tables, cleanup cron, orphan detection
- **No timeout semantics** — job hangs forever, client gives up, server keeps working
- **No human gates** — what if a report needs manager approval before delivery?

---

## The Solution: Intent Lifecycle

```
Client → send_intent("generate report") → intent_id
Client → observe(intent_id)  ← real-time SSE stream

Server: CREATED → SUBMITTED → DELIVERED → IN_PROGRESS → COMPLETED
```

One call to submit, one stream to watch. The platform handles retries, timeouts, and delivery guarantees.

---

## Quick Start

### Python

```bash
pip install axme
export AXME_API_KEY="your-key"   # Get one: axme login
```

```python
from axme import AxmeClient, AxmeClientConfig
import os

client = AxmeClient(AxmeClientConfig(api_key=os.environ["AXME_API_KEY"]))

# Submit a long-running operation
intent_id = client.send_intent({
    "intent_type": "report.generate.v1",
    "to_agent": "agent://myorg/production/report-service",
    "payload": {"report_type": "quarterly", "format": "pdf"},
})

print(f"Submitted: {intent_id}")

# Wait for completion — no polling, no webhooks
result = client.wait_for(intent_id)
print(f"Done: {result['status']}")
```

### TypeScript

```bash
npm install @axme/axme
```

```typescript
import { AxmeClient } from "@axme/axme";

const client = new AxmeClient({ apiKey: process.env.AXME_API_KEY! });

const intentId = await client.sendIntent({
  intentType: "report.generate.v1",
  toAgent: "agent://myorg/production/report-service",
  payload: { reportType: "quarterly", format: "pdf" },
});

console.log(`Submitted: ${intentId}`);

const result = await client.waitFor(intentId);
console.log(`Done: ${result.status}`);
```

---

## More Languages

Full implementations in all 5 languages:

| Language | Directory | Install |
|----------|-----------|---------|
| [Python](python/) | `python/` | `pip install axme` |
| [TypeScript](typescript/) | `typescript/` | `npm install @axme/axme` |
| [Go](go/) | `go/` | `go get github.com/AxmeAI/axme-sdk-go` |
| [Java](java/) | `java/` | Maven Central: `ai.axme:axme-sdk` |
| [.NET](dotnet/) | `dotnet/` | `dotnet add package Axme.Sdk` |

---

## Before / After

### Before: Polling + Webhooks (200+ lines)

```python
# Job submission endpoint
@app.post("/reports/generate")
async def generate(req):
    job_id = str(uuid4())
    redis.set(f"job:{job_id}", "pending")
    queue.enqueue(generate_report, job_id, req.params)
    return {"job_id": job_id, "status": "pending"}

# Polling endpoint (client hits this 50 times)
@app.get("/reports/status/{job_id}")
async def status(job_id):
    state = redis.get(f"job:{job_id}")
    if not state:
        raise HTTPException(404)
    return {"job_id": job_id, "status": state}

# Webhook callback (fails silently, needs retry logic)
@app.post("/webhooks/report-done")
async def webhook(req):
    # Verify signature... retry on failure... dead letter queue...
    pass

# Plus: Redis cleanup cron, orphan job detector, timeout handler...
```

### After: AXME Intent Lifecycle (15 lines)

```python
from axme import AxmeClient, AxmeClientConfig

client = AxmeClient(AxmeClientConfig(api_key=os.environ["AXME_API_KEY"]))

intent_id = client.send_intent({
    "intent_type": "report.generate.v1",
    "to_agent": "agent://myorg/production/report-service",
    "payload": {"report_type": "quarterly", "format": "pdf"},
})

result = client.wait_for(intent_id)
print(result["status"])  # COMPLETED, FAILED, or TIMED_OUT
```

No Redis. No polling endpoint. No webhook handler. No cleanup cron. No orphan detector.

---

## How It Works

```
┌────────────┐  send_intent()   ┌────────────────┐   deliver    ┌──────────────┐
│            │ ───────────────> │                │ ──────────> │              │
│   Client   │                  │   AXME Cloud   │              │   Service    │
│            │ <── observe() ── │   (platform)   │ <─ resume()  │   (agent)    │
│            │  real-time SSE   │                │  with result │              │
└────────────┘                  │   retries,     │              │  processes   │
                                │   timeouts,    │              │  the work    │
                                │   delivery     │              │              │
                                └────────────────┘              └──────────────┘
```

1. Client submits an **intent** — a request that completes later
2. Platform **delivers** it to the target service/agent
3. Service processes and **resumes** with result
4. Client **observes** lifecycle events in real time (SSE stream)
5. Platform handles retries, timeouts, and delivery guarantees

---

## Run the Full Example

```bash
# Install CLI (one-time)
curl -fsSL https://raw.githubusercontent.com/AxmeAI/axme-cli/main/install.sh | sh
source ~/.zshrc

# Log in
axme login

# Run the built-in example
axme examples run delivery/stream
```

---

## Related

- [AXME](https://github.com/AxmeAI/axme) — project overview
- [AXP Spec](https://github.com/AxmeAI/axme-spec) — open Intent Protocol specification
- [AXME Examples](https://github.com/AxmeAI/axme-examples) — 20+ runnable examples across 5 languages
- [AXME CLI](https://github.com/AxmeAI/axme-cli) — manage intents, agents, scenarios from the terminal

---

Built with [AXME](https://github.com/AxmeAI/axme) (AXP Intent Protocol).
