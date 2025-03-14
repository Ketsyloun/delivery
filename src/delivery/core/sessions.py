from fastapi import Request, Response
import uuid
import json

from delivery.config.redis_config import get_redis_connection


async def get_session(response: Response,
                      request: Request) -> list[int]:
    r = await get_redis_connection()
    session_id = request.cookies.get("session_id")
    if session_id and await r.exists(session_id):
        session_data_bytes = await r.get(session_id)
        session_data = json.loads(session_data_bytes.decode())
        await r.close()
        return session_data
    new_session_id = str(uuid.uuid4())
    await r.setex(new_session_id, 7 * 24 * 60 * 60, json.dumps([]))
    response.set_cookie("session_id", new_session_id, httponly=True)
    await r.close()
    return []


async def post_session(parcel_id: int, response: Response,
                       request: Request) -> str:
    r = await get_redis_connection()
    session_id = request.cookies.get("session_id")
    if session_id and await r.exists(session_id):
        session_data = json.loads(await r.get(session_id))
        session_data.append(parcel_id)
        await r.setex(session_id, 7*24*60*60, json.dumps(session_data))
        await r.close()
        return session_id

    new_session_id = str(uuid.uuid4())
    await r.setex(new_session_id, 7*24*60*60, json.dumps([parcel_id]))
    response.set_cookie("session_id", new_session_id, httponly=True)
    await r.close()
    return new_session_id
