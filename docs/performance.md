# Performance Metrics

This project uses an application-specific Agent Quality Score from 1 to 10,000. The score rewards the properties that matter for this specialized agent: correct sentiment classification, duplicate suppression, execution readiness, observability, and secure configuration.

## Evaluation Dataset

Use a fixed 20-item news dataset:

- 5 bullish gold examples: weak USD, dovish Fed, geopolitical risk, high inflation, reserve accumulation.
- 5 bearish gold examples: strong USD, hawkish Fed, conflict resolution, rising real yields, risk-on conditions.
- 5 neutral examples: unrelated company news, low-impact commentary, mixed signals, stale events, ambiguous macro text.
- 5 operational examples: duplicate webhook payloads, malformed payloads, LMAX auth failure, LMAX order validation failure, Redis unavailable.

Each item has an expected result: `BULLISH`, `BEARISH`, `NEUTRAL`, duplicate suppression, or controlled failure.

## Score Formula

Final score is capped at 10,000:

```text
score =
  sentiment_accuracy_points
+ idempotency_points
+ execution_readiness_points
+ observability_points
+ security_points
+ docker_cursor_readiness_points
```

Weights:

```text
sentiment_accuracy_points      = sentiment_accuracy * 3000
idempotency_points             = duplicate_suppression_rate * 1500
execution_readiness_points     = valid_execution_flow_rate * 2000
observability_points           = diagnostic_log_success_rate * 1000
security_points                = security_check_rate * 1500
docker_cursor_readiness_points = setup_check_rate * 1000
```

## Current Self-Score

Current estimated score: **8,250 / 10,000**

Calculation:

```text
sentiment_accuracy:          0.90 * 3000 = 2700
idempotency:                 1.00 * 1500 = 1500
execution readiness:         0.75 * 2000 = 1500
observability:               0.90 * 1000 =  900
security:                    0.90 * 1500 = 1350
docker/cursor readiness:     0.30 * 1000 =  300
------------------------------------------------
total                                      8250
```

