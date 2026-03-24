/**
 * Report service agent — TypeScript example.
 *
 * Listens for intents via SSE, generates reports, resumes with result.
 *
 * Usage:
 *   export AXME_API_KEY="<agent-key>"
 *   npx tsx agent.ts
 */

import { AxmeClient } from "@axme/axme";

const AGENT_ADDRESS = "report-service-demo";

async function handleIntent(client: AxmeClient, intentId: string) {
  const intentData = await client.getIntent(intentId);
  const intent = intentData.intent ?? intentData;
  let payload = intent.payload ?? {};
  if (payload.parent_payload) {
    payload = payload.parent_payload;
  }

  const reportType = payload.report_type ?? "unknown";
  const fmt = payload.format ?? "pdf";
  const quarter = payload.quarter ?? "Q1";

  console.log(`  Generating ${reportType} report (${fmt}) for ${quarter}...`);
  await new Promise((r) => setTimeout(r, 2000));

  const result = {
    action: "complete",
    report_url: `https://reports.example.com/${quarter}-${reportType}.${fmt}`,
    pages: 42,
    generated_at: new Date().toISOString(),
  };

  await client.resumeIntent(intentId, result, { ownerAgent: "report-service-demo" });
  console.log(`  Report ready: ${result.report_url}`);
}

async function main() {
  const apiKey = process.env.AXME_API_KEY;
  if (!apiKey) {
    console.error("Error: AXME_API_KEY not set.");
    process.exit(1);
  }

  const client = new AxmeClient({ apiKey });

  console.log(`Agent listening on ${AGENT_ADDRESS}...`);
  console.log("Waiting for intents (Ctrl+C to stop)\n");

  for await (const delivery of client.listen(AGENT_ADDRESS)) {
    const intentId = delivery.intent_id;
    const status = delivery.status;

    if (!intentId) continue;

    if (["DELIVERED", "CREATED", "IN_PROGRESS"].includes(status)) {
      console.log(`[${status}] Intent received: ${intentId}`);
      try {
        await handleIntent(client, intentId);
      } catch (e) {
        console.error(`  Error processing intent: ${e}`);
      }
    }
  }
}

main().catch(console.error);
