import os
import aioredis
import redis
from dotenv import load_dotenv

load_dotenv()


async def get_redis_connection():
    redis_url = f"redis://{os.getenv('HOST_REDIS')}:{os.getenv('PORT_REDIS')}"

    r = await aioredis.from_url(
        redis_url,
        db=int(os.getenv("DB_REDIS"))
    )
    return r

r = redis.Redis(host=os.getenv("HOST_REDIS"), 
                port=int(os.getenv("PORT_REDIS")),
                db=int(os.getenv("DB_REDIS")))
