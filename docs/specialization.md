# Problem Specialization

## Specialized Problem

This agent specializes in event-driven macro news trading for XAU/USD. It receives a news webhook, classifies the likely gold-market direction, deduplicates repeated events, and routes a fixed market order to LMAX when the signal is actionable.

## Why This Problem

Macro news can move gold quickly, but manual interpretation is slow and inconsistent. A small, auditable agent is a good fit because the workflow has clear inputs, clear outputs, and high value from low latency:

- Input: timestamped news text.
- Reasoning: classify the macro impact on gold.
- Safety: suppress duplicate events and fail closed on execution errors.
- Output: structured decision plus optional order routing.

## Why This Was Priority #1

The highest-risk part of an AI trading workflow is not generating an opinion. It is turning an opinion into an execution decision safely. This project prioritizes the complete operational loop: model decision, idempotency, authentication, payload validation, and logs that make failures explainable.

## Design Decisions

- FastAPI provides a simple webhook interface and OpenAPI docs.
- Redis prevents duplicate news events from creating duplicate trades.
- Gemini produces structured JSON matching a Pydantic schema.
- LMAX integration is isolated in one client module so authentication and order placement stay auditable.
- Docker Compose runs the API and Redis together for reproducible demos.
- Cursor rules document the project-specific constraints for future AI-assisted edits.
