import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

redis_conn = redis.Redis(
    host=REDIS_HOST,  # type: ignore
    port=int(REDIS_PORT),  # type: ignore
    password=REDIS_PASSWORD,
    decode_responses=True,
    username="default",
)
