import os
from typing import Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from src.log import get_logger

logger = get_logger(__name__)

class SentimentAnalysis(BaseModel):
    """
    Pydantic schema defining the exact deterministic JSON structure 
    required from the Gemini inference engine. This maps to OpenAPI schemas.
    """
    market_direction: Literal["BULLISH", "BEARISH", "NEUTRAL"] = Field(
        description="The predicted movement of the XAU/USD market."
    )
    reasoning: str = Field(
        description="A concise 1-2 sentence justification for the macroeconomic decision."
    )

class GenerativeEngine:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        
        # Initialize the official Google GenAI SDK client
        self.client = genai.Client(api_key=api_key)
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        
        # The prompt defines the exact macroeconomic mandate for Gold trading
        self.system_prompt = (
            "You are an expert quantitative macro-economist trading the XAU/USD (Spot Gold) instrument. "
            "Analyze the following news text. If the news implies a weakening US Dollar, geopolitical "
            "instability, or dovish central bank policy, classify it as BULLISH for gold. If the news "
            "implies a strengthening US Dollar, resolved conflicts, or hawkish central bank policy, "
            "classify it as BEARISH. If the impact is negligible, classify it as NEUTRAL."
        )

    def evaluate_sentiment(self, news_text: str) -> SentimentAnalysis:
        """
        Executes a synchronous, structurally constrained inference call to the Gemini API.
        """
        try:
            logger.info(
                "Transmitting payload to Gemini API for evaluation.",
                extra={"model": self.model_id},
            )
            
            # Request strict JSON output conforming to the Pydantic schema
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=f"System Mandate: {self.system_prompt}\n\nNews: {news_text}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SentimentAnalysis,
                    temperature=0.0 # Force greedy decoding for maximum determinism
                ),
            )
            
            # The output is strictly guaranteed to conform to the schema
            # We parse the raw JSON string back into our robust Pydantic object
            result = SentimentAnalysis.model_validate_json(response.text)
            
            logger.info("Inference completed successfully.", extra={
                "direction": result.market_direction,
                "reasoning": result.reasoning
            })
            
            return result
            
        except Exception:
            logger.exception(
                "Generative AI inference failed.",
                extra={"model": self.model_id},
            )
            raise
