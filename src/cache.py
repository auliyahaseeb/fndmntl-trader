import hashlib
import redis
import os
from src.log import get_logger

logger = get_logger(__name__)

class IdempotencyCache:
    """
    Manages state and distributed locking using Redis.
    Guarantees 'at-most-once' execution semantics for incoming webhooks.
    """
    def __init__(self) -> None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        try:
            # decode_responses=True ensures strings are returned instead of bytes
            self.client = redis.Redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            logger.info("Successfully connected to Redis state backend.")
        except redis.ConnectionError as e:
            logger.error("Failed to connect to Redis.", extra={"error": str(e)})
            raise

    def check_and_lock(self, text_payload: str) -> bool:
        """
        Hashes the incoming payload and attempts to acquire a lock via SETNX.
        Returns True if the event is unique and the lock was acquired.
        Returns False if the event is a duplicate.
        """
        # Generate a 256-bit cryptographic digest of the exact text payload
        digest = hashlib.sha256(text_payload.encode('utf-8')).hexdigest()
        lock_key = f"trade_lock:{digest}"
        
        # Attempt to set the key if it does not exist (SETNX operation)
        # TTL is strictly enforced at 86400 seconds (24 hours) to prevent memory leaks
        acquired = self.client.set(lock_key, "LOCKED", nx=True, ex=86400)
        
        if acquired:
            logger.info("Idempotency lock acquired. Proceeding with event.", extra={"hash": digest})
            return True
        else:
            logger.warning("Duplicate event detected. Lock denied.", extra={"hash": digest})
            return False