import asyncio
import os
import requests
from celery.signals import worker_ready
from dotenv import load_dotenv
from sqlalchemy import insert

from delivery.config.celery_config import app
from delivery.config.redis_config import r
from delivery.parcels.models import Parcels
from delivery.database import asyncs_session_maker

load_dotenv()


@app.task
def getting_the_dollar_rate():
    response = requests.get(os.getenv("URL_USD"))
    data = response.json()
    usd_rate = data['Valute']['USD']['Value']
    r.set('usd_rate', usd_rate)
    return usd_rate


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    getting_the_dollar_rate.apply_async()
    if not r.exists("parcel_id"):
        r.set("parcel_id", 0)


@app.task
def post_parcel(parcel: dict, parcel_id: int):
    shipping_cost = (
        parcel["weight"] * 0.05 + parcel["parcel_value"] * 0.01
    ) * float(r.get('usd_rate'))
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(post_req(parcel, parcel_id, shipping_cost))
    else:
        loop.run_until_complete(post_req(parcel, parcel_id, shipping_cost))


async def post_req(parcel: dict, parcel_id: int, shipping_cost):
    async with asyncs_session_maker() as session:
        req = insert(Parcels).values(
            id=parcel_id,
            name=parcel["name"],
            weight=parcel["weight"],
            type_id=parcel["type_id"],
            parcel_value=parcel["parcel_value"],
            shipping_cost=shipping_cost
        )
        await session.execute(req)
        await session.commit()