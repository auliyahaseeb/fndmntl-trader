import os
import base64
import binascii
import hashlib
import hmac
import uuid
import httpx
from datetime import datetime, timezone
from src.log import get_logger

logger = get_logger(__name__)

TIME_IN_FORCE_ALIASES = {
    "GTC": "GOOD_TIL_CANCELLED",
    "FOK": "FILL_OR_KILL",
    "GFD": "GOOD_FOR_DAY",
    "IOC": "IMMEDIATE_OR_CANCEL",
}

class LmaxClient:
    def __init__(self) -> None:
        self.base_url = (os.getenv("LMAX_URL") or "").strip().rstrip("/")
        self.client_key_id = (os.getenv("LMAX_API_KEY") or "").strip()
        self.secret = (os.getenv("LMAX_SECRET") or "").strip()
        self.instrument_id = "xau-usd"
        configured_time_in_force = (os.getenv("LMAX_TIME_IN_FORCE") or "IMMEDIATE_OR_CANCEL").strip().upper()
        self.time_in_force = TIME_IN_FORCE_ALIASES.get(
            configured_time_in_force,
            configured_time_in_force,
        )
        self.session_token = None

        if not all([self.base_url, self.client_key_id, self.secret]):
            raise ValueError("LMAX configuration environment variables are incomplete.")

        self.http_client = httpx.Client(timeout=httpx.Timeout(10.0))

    def get_server_time(self) -> str:
        """
        Fetches the current server time from LMAX to ensure the 30s window is met.
       
        """
        endpoint = f"{self.base_url}/v1/time"
        response = self.http_client.get(endpoint)
        response.raise_for_status()
        # Returns the server's ISO8601 timestamp directly
        return response.json().get("timestamp")

    def _generate_signature(self, nonce: str, timestamp: str) -> str:
        """
        Generates the mandatory base64-encoded HMAC-SHA256 signature for LMAX.
        Handshake message: client_key_id + nonce + timestamp.
        """
        message = f"{self.client_key_id}{nonce}{timestamp}"

        try:
            decoded_secret = base64.b64decode(self.secret, validate=True)
        except binascii.Error as e:
            raise ValueError("LMAX_SECRET must be a valid base64-encoded secret.") from e

        signature_digest = hmac.new(
            decoded_secret,
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        return base64.b64encode(signature_digest).decode('utf-8')

    def authenticate(self) -> None:
        """
        Executes the cryptographic handshake with LMAX.
        """
        endpoint = f"{self.base_url}/v1/authenticate"
        
        # LMAX nonces must be unique within a 60-second window
        # Using a full UUID ensures uniqueness
        nonce = uuid.uuid4().hex
        
        try:
            # Sync with the LMAX server time to ensure the 30s window is met
            timestamp = self.get_server_time()
            
            signature = self._generate_signature(nonce, timestamp)
            
            payload = {
                "client_key_id": self.client_key_id,
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": signature
            }
            
            # Use the official JSON payload for authentication
            response = self.http_client.post(endpoint, json=payload)
            
            if response.status_code != 200:
                logger.error("LMAX authentication rejected.", extra={
                    "status": response.status_code,
                    "server_response": response.text,
                    "sent_timestamp": timestamp
                })
            
            response.raise_for_status()
            
            data = response.json()
            self.session_token = data.get("token")
            logger.info("Successfully acquired LMAX session bearer token.")
            
        except Exception as e:
            logger.error("LMAX authentication logic failed.", extra={"error": str(e)})
            raise

    def execute_fixed_trade(self, direction: str) -> None:
        """
        Maps the AI sentiment directive to a fixed market order.
        """
        if direction not in ["BULLISH", "BEARISH"]:
            logger.info("Neutral direction received. Trading execution bypassed.")
            return

        if not self.session_token:
            self.authenticate()

        side = "BID" if direction == "BULLISH" else "ASK"
        quantity = "10.0"
        instruction_id = uuid.uuid4().hex[:20]

        endpoint = f"{self.base_url}/v1/account/place-order"
        headers = {
            "Authorization": f"Bearer {self.session_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "instrument_id": self.instrument_id,
            "type": "MARKET",
            "side": side,
            "quantity": quantity,
            "time_in_force": self.time_in_force,
            "instruction_id": instruction_id,
        }

        try:
            logger.info(
                "Transmitting MARKET order to LMAX Exchange.",
                extra={
                    "side": side,
                    "quantity": quantity,
                    "time_in_force": self.time_in_force,
                    "instruction_id": instruction_id,
                },
            )

            response = self.http_client.post(endpoint, headers=headers, json=payload)

            if response.status_code == 401:
                logger.warning("Session token expired. Attempting LMAX re-authentication.")
                self.authenticate()
                headers["Authorization"] = f"Bearer {self.session_token}"
                response = self.http_client.post(endpoint, headers=headers, json=payload)

            response.raise_for_status()
            logger.info(
                "Order successfully acknowledged by LMAX matching engine.",
                extra={"response": response.json()},
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                "Order rejection returned by LMAX.",
                extra={"status_code": e.response.status_code, "detail": e.response.text},
            )
            raise
        except httpx.RequestError as e:
            logger.error("Network layer failure during execution routing.", extra={"error": str(e)})
            raise
