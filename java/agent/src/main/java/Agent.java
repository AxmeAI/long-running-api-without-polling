/*
 * Report service agent — Java example.
 *
 * Fetches an intent by ID, generates a report, and resumes with result.
 *
 * Usage:
 *   export AXME_API_KEY="<agent-key>"
 *   javac -cp axme-sdk.jar Agent.java
 *   java -cp .:axme-sdk.jar Agent <intent_id>
 */

import dev.axme.sdk.AxmeClient;
import dev.axme.sdk.AxmeClientConfig;
import dev.axme.sdk.RequestOptions;
import java.time.Instant;
import java.util.Map;

public class Agent {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("Usage: java Agent <intent_id>");
            System.exit(1);
        }

        String apiKey = System.getenv("AXME_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Error: AXME_API_KEY not set.");
            System.exit(1);
        }

        String intentId = args[0];
        var client = new AxmeClient(AxmeClientConfig.forCloud(apiKey));

        System.out.println("Processing intent: " + intentId);

        // Fetch the intent
        var intentData = client.getIntent(intentId, new RequestOptions());
        @SuppressWarnings("unchecked")
        var intent = (Map<String, Object>) intentData.getOrDefault("intent", intentData);
        @SuppressWarnings("unchecked")
        var payload = (Map<String, Object>) intent.getOrDefault("payload", Map.of());
        if (payload.containsKey("parent_payload")) {
            @SuppressWarnings("unchecked")
            var pp = (Map<String, Object>) payload.get("parent_payload");
            payload = pp;
        }

        String reportType = (String) payload.getOrDefault("report_type", "unknown");
        String fmt = (String) payload.getOrDefault("format", "pdf");
        String quarter = (String) payload.getOrDefault("quarter", "Q1");

        System.out.println("  Generating " + reportType + " report (" + fmt + ") for " + quarter + "...");
        Thread.sleep(2000);

        String reportUrl = "https://reports.example.com/" + quarter + "-" + reportType + "." + fmt;
        var result = Map.<String, Object>of(
            "action", "complete",
            "report_url", reportUrl,
            "pages", 42,
            "generated_at", Instant.now().toString()
        );

        client.resumeIntent(intentId, result, new RequestOptions());
        System.out.println("  Report ready: " + reportUrl);
    }
}
