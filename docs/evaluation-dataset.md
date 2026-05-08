# Evaluation Dataset

Use these cases to score the agent. Each input should be submitted to `POST /webhook/news`.

| ID | News summary | Expected result |
| --- | --- | --- |
| B1 | US Dollar weakens after soft CPI data | BULLISH |
| B2 | Central banks increase gold reserves | BULLISH |
| B3 | Geopolitical tensions escalate | BULLISH |
| B4 | Fed signals rate cuts | BULLISH |
| B5 | Inflation remains above target | BULLISH |
| S1 | US Dollar rallies after strong payrolls | BEARISH |
| S2 | Fed signals higher-for-longer policy | BEARISH |
| S3 | Peace agreement reduces safe-haven demand | BEARISH |
| S4 | Real yields rise sharply | BEARISH |
| S5 | Risk assets rally as volatility falls | BEARISH |
| N1 | Local company announces product launch | NEUTRAL |
| N2 | Mixed Fed comments with no policy shift | NEUTRAL |
| N3 | Analyst repeats old gold forecast | NEUTRAL |
| N4 | Weather report unrelated to markets | NEUTRAL |
| N5 | Minor commodity update with no USD impact | NEUTRAL |
| O1 | Same payload sent twice | Second request ignored |
| O2 | Missing `news_text` field | FastAPI validation error |
| O3 | Invalid Gemini key | Controlled 500 with provider trace in logs |
| O4 | Invalid LMAX signature | Controlled 500 with LMAX response in logs |
| O5 | Redis unavailable | Startup or request failure with Redis log |

Scoring details are in [performance.md](performance.md).
