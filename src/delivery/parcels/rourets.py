from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from .dao import ParcelsDao, ParcelsTypeDao
from .schemas import SParcels, SParcelsPost, create_sparcel
from delivery.config.redis_config import get_redis_connection
from delivery.core.celery_tasks import post_parcel
from delivery.core.sessions import get_session, post_session

router = APIRouter(
    prefix='/parcels',
    tags=["Бронирование"],
)


@router.get("")
async def get_parsels(type: Optional[str] = None,
                      page: Optional[int] = Query(0, ge=0),
                      size: Optional[int] = Query(None, ge=1, le=1000),
                      parcel_id: list[int] = Depends(get_session)
                      ) -> Union[list[SParcels], str]:
    if not parcel_id:
        return "Вы не отправили ни одной посылки"
    parcels = await ParcelsDao.find_all(parcel_id, type, page, size)
    return [create_sparcel(parcel) for parcel in parcels]


@router.get("/types")
async def get_parsels_type():
    return await ParcelsTypeDao.find_all()


@router.get("/hotels")
async def get_hotels():
    r = await get_redis_connection()
    usd_rate = await r.get('usd_rate')
    return {"usd_rate": usd_rate}


@router.get("/redis/all")
async def get_all_redis_keys():
    r = await get_redis_connection()
    keys = await r.keys("*")
    data = {}
    for key in keys:
        value = await r.get(key)
        data[key] = value

    return data


@router.post("")
async def post_parsels(parcel: SParcelsPost,
                       response: Response,
                       request: Request) -> Union[dict, str]:
    r = await get_redis_connection()
    parcel_id = await r.incr("parcel_id")
    parcel_data = parcel.model_dump()
    if not await ParcelsTypeDao.find_one_or_none(id=parcel.type_id):
        await r.decr("parcel_id")
        raise HTTPException(
            status_code=400,
            detail=f"Тип посылки с ID {parcel.type_id} не существует в базе данных."
        )
    post_parcel.delay(parcel_data, parcel_id)
    await post_session(parcel_id, response, request)
    await r.close()
    return {"id": parcel_id}


@router.get("/{parcel_id}")
async def get_parsels_id(parcel_id: int,
                         parcels_id: list[int] = Depends(get_session)
                         ) -> Union[SParcels, str]:
    if parcel_id in parcels_id:
        parcel = await ParcelsDao.find_by_id(model_id=parcel_id)
        return create_sparcel(parcel)
    else:
        return f"Послыка с id = {parcel_id} отправлена другим пользвателем"