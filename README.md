# Fundamental Trader Agent

Fundamental Trader Agent is a Cursor-ready AI agent for event-driven XAU/USD trading. It receives macro news through a FastAPI webhook, classifies the likely gold-market direction with Gemini, suppresses duplicate events with Redis, and routes actionable signals to LMAX.

## Specialized Problem

The agent is specialized for macroeconomic news that affects spot gold. It focuses on events such as weak or strong USD, central bank policy, inflation, geopolitical risk, and market volatility.

This was chosen as the top priority because trading agents need more than model output. They need a controlled execution pipeline with idempotency, authentication, payload validation, and useful logs when something fails.

## Console LOG


<img width="1265" height="272" alt="image" src="https://github.com/user-attachments/assets/ee4cfe48-0193-42b4-9a30-358ce635c852" />


## LMAX Trade




<img width="853" height="136" alt="Screenshot 2026-05-08 100035" src="https://github.com/user-attachments/assets/9d6bd4cf-63dc-46ee-9ea6-8c965594fb75" />












## Capabilities

- FastAPI webhook endpoint at `POST /webhook/news`.
- Gemini structured JSON sentiment classification.
- Redis idempotency lock to prevent duplicate trade execution.
- LMAX authentication and fixed market-order routing.
- Structured JSON logs for API, cache, LLM, and execution steps.
- Docker Compose setup for reproducible local runs.
- Cursor configuration through `.cursorrules` and `.cursor/rules/trader-agent.mdc`.

## Architecture

```text
News webhook
  -> FastAPI payload validation
  -> Redis duplicate lock
  -> Gemini sentiment classification
  -> LMAX authentication
  -> LMAX market order, if BULLISH or BEARISH
```

## Cursor Setup

This project includes:

- `.cursorrules`
- `.cursor/rules/trader-agent.mdc`

These files tell Cursor how to work safely in this repository. The rules emphasize secret hygiene, deterministic trading flow, structured logs, Docker readiness, and careful handling of LMAX execution code.

## Environment Variables

Create a local `.env` file from the example:

```powershell
copy .env.example .env
```

Required values:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

LMAX_API_KEY=your_lmax_client_id_here
LMAX_SECRET=your_lmax_base64_secret_here
LMAX_URL=https://account-api.london-demo.lmax.com
LMAX_TIME_IN_FORCE=IMMEDIATE_OR_CANCEL

REDIS_URL=redis://redis:6379/0
```

Never commit `.env`. It is ignored by git.

## Run With Docker

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:8000/docs
```

Stop:

```powershell
docker compose down
```

If your Docker installation uses the legacy command:

```powershell
docker-compose up --build
```

## Example Webhook Payload

```json
{
  "news_text": "Central banks are increasing gold reserves as inflation remains high and the US Dollar weakens.",
  "timestamp": "2026-05-08T14:30:00Z"
}
```

Expected response shape:

```json
{
  "status": "processed",
  "direction": "BULLISH",
  "reasoning": "..."
}
```

## Performance Score

Current self-evaluation: **8,250 / 10,000**.

The score is calculated from:

- Sentiment accuracy.
- Duplicate suppression.
- Execution readiness.
- Observability.
- Security.
- Docker and Cursor readiness.

Full scoring method: [docs/performance.md](docs/performance.md)

Evaluation cases: [docs/evaluation-dataset.md](docs/evaluation-dataset.md)

## Benchmark Against Default Cursor Claude

The agent is compared with default Cursor Claude on domain-specific workflow tasks such as weak-USD classification, duplicate webhook suppression, Gemini failure diagnosis, LMAX auth debugging, and order validation.

Full benchmark: [docs/benchmark.md](docs/benchmark.md)

## Security

- Secrets are loaded from environment variables.
- `.env` is ignored by git.
- Logs do not print API keys, LMAX secrets, or bearer tokens.
- `.env.example` uses placeholders only.
- Docker uses `env_file` for runtime configuration.
