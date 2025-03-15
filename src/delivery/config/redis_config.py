import os
import aioredis
import redis
from dotenv import load_dotenv

load_dotenv()


async def get_redis_connection():
    r = await aioredis.from_url(os.getenv("REDIS_URL"))
    return r

r = redis.Redis(host=os.getenv("HOST_REDIS"),
                port=int(os.getenv("PORT_REDIS")),
                db=int(os.getenv("DB_REDIS")))
