# Benchmark Comparison

This comparison evaluates the custom Fundamental Trader Agent against default Cursor with Claude in a plain coding assistant role.

## Test Cases

| Test case | Fundamental Trader Agent | Default Cursor Claude |
| --- | --- | --- |
| Classify weak USD gold news | Uses a fixed XAU/USD macro prompt and returns `BULLISH` with concise reasoning | Can classify correctly, but may require the user to restate domain rules |
| Duplicate webhook payload | Redis idempotency lock suppresses duplicate execution | No built-in duplicate suppression unless implemented during the session |
| Gemini model/key failure | Structured JSON logs expose model and provider exception | Helpful debugging, but no project-specific logging contract by default |
| LMAX auth signature mismatch | Code contains dedicated HMAC signing path and LMAX response logging | Can help debug, but starts without exchange-specific assumptions |
| LMAX order validation error | Logs exact response body and payload context without secrets | Can infer fixes from logs, but no prebuilt trading payload path |
| Docker startup | Compose starts API plus Redis with `.env` configuration | Can create Docker setup, but not specialized until prompted |

## Side-by-Side Summary

| Category | This Agent | Default Cursor Claude |
| --- | --- | --- |
| Specialization | XAU/USD macro sentiment and LMAX routing | General software development assistant |
| Runtime behavior | Executes a complete webhook-to-order pipeline | Produces/edit code but does not run an embedded domain workflow |
| Safety posture | Fails closed on missing config, auth failure, or order rejection | Depends on prompts and local implementation |
| Observability | Structured JSON logs for pipeline, LLM, Redis, and LMAX | No default app-level telemetry |
| Weakness | Requires valid external credentials and LMAX API compatibility | More flexible for unrelated tasks |

## Where This Agent Excels

The agent excels when the problem is narrow: converting macroeconomic news into deterministic gold-trading actions while preserving auditability. It does not try to be a general coding assistant. Its advantage is that the trading workflow, failure modes, environment variables, and execution rules are encoded in the application and Cursor rules.

## Where Default Cursor Claude Excels

Default Cursor Claude is stronger for broad, open-ended software tasks such as refactoring an unfamiliar frontend, writing general tests, or exploring a new architecture. It is less constrained, which is useful outside this trading domain.
