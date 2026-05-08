from fastapi import FastAPI, HTTPException, status
import os
from pathlib import Path
import uvicorn
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(path: str = ".env") -> None:
        env_path = next(
            (parent / path for parent in [Path.cwd(), *Path.cwd().parents] if (parent / path).exists()),
            None,
        )
        if env_path is None:
            return
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip("\"'")
else:
    def load_local_dotenv(path: str = ".env") -> None:
        load_dotenv(path, override=True)

if "load_local_dotenv" in globals():
    load_local_dotenv()
else:
    load_dotenv()

from src.log import get_logger
from src.cache import IdempotencyCache
from src.llm import GenerativeEngine
from src.lmax_client import LmaxClient

logger = get_logger(__name__)

# Initialize singletons at startup to ensure persistence across requests
app = FastAPI(title="Event-Driven AI Sentiment Trader")
idempotency_store = IdempotencyCache()
ai_engine = GenerativeEngine()
execution_client = LmaxClient()

class NewsPayload(BaseModel):
    """
    Pydantic schema for the incoming webhook payload.
    Ensures input validation prior to processing.
    """
    news_text: str
    timestamp: str

@app.post("/webhook/news", status_code=status.HTTP_200_OK)
async def process_news_webhook(payload: NewsPayload):
    """
    Primary ingestion endpoint. Orchestrates the flow:
    Hash Check -> AI Sentiment Inference -> LMAX Execution.
    """
    logger.info("Webhook payload received.", extra={"timestamp": payload.timestamp})

    # Step 1: Distributed Idempotency Verification
    if not idempotency_store.check_and_lock(payload.news_text):
        # 200 OK returned early to acknowledge receipt without duplicate processing
        return {"status": "ignored", "reason": "Duplicate event suppressed via Redis lock."}

    try:
        # Step 2: Deterministic Sentiment Inference
        sentiment_result = ai_engine.evaluate_sentiment(payload.news_text)

        # Step 3: High-Reliability Order Routing
        if sentiment_result.market_direction in ["BULLISH", "BEARISH"]:
            execution_client.execute_fixed_trade(sentiment_result.market_direction)

        return {
            "status": "processed",
            "direction": sentiment_result.market_direction,
            "reasoning": sentiment_result.reasoning
        }

    except Exception:
        logger.exception("Pipeline failure encountered.")
        # Emit a 500 so upstream alerting identifies processing failures
        raise HTTPException(status_code=500, detail="Internal processing failure.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
