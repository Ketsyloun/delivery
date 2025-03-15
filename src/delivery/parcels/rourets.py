import sys
from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from loguru import logger

from .dao import ParcelsDao, ParcelsTypeDao
from .schemas import (SParcels, SParcelsPost,
                      create_sparcel, SParcelsType, SMessage)
from delivery.config.redis_config import get_redis_connection
from delivery.core.celery_tasks import post_parcel
from delivery.core.sessions import get_session, post_session


router = APIRouter(
    prefix='/parcels',
    tags=["Посылки"],
)

logger.remove()
logger.add(sys.stdout, format="{message}", level="INFO", serialize=True)


@router.get("")
async def get_parsels(type: Optional[str] = None,
                      page: Optional[int] = Query(0, ge=0),
                      size: Optional[int] = Query(None, ge=1, le=1000),
                      parcel_id: list[int] = Depends(get_session)
                      ) -> Union[list[SParcels], SMessage]:
    """Получение списка всех посылок, отправленных пользователем.

    **Аргументы**:  
        - type (str, optional): Тип посылки для сортировки. По умолчанию не указан.  
        - page (int, optional): Номер страницы для пагинации. По умолчанию 0. Минимальное значение: 0.  
        - size (int, optional): Количество посылок на странице. Минимальное значение: 1, максимальное: 1000.  

    **Возвращаемый результат**:  
        - Если у пользователя есть отправленные посылки, возвращается список посылок.  
        - Если посылок нет, возвращается сообщение.
    """
    if not parcel_id:
        logger.info({"message": "Не получено ни одной посылки в запросе"})
        return {"message": "Вы не отправили ни одной посылки"}
    parcels = await ParcelsDao.find_all(parcel_id, type, page, size)
    logger.info({"message": f"Пользователь получил послылки с id = {parcel_id}"})
    return [create_sparcel(parcel) for parcel in parcels]


@router.get("/types")
async def get_parsels_type() -> list[SParcelsType]:
    """Получение списка типа посылок

    **Возвращаемый результат**:  
        - Список типов посылок с уникальным id
    """
    logger.info({"message": "Получены все типо посылок"})
    return await ParcelsTypeDao.find_all()


@router.post("")
async def post_parsels(parcel: SParcelsPost,
                       response: Response,
                       request: Request) -> SMessage:
    """Запрос на регистрацию новой посылки.

    **Аргументы**:  
        - parcel: Данные о посылке в формате JSON

    **Исключения**:  
        - HTTPException: Исключение при введение несуществующего id типа посылки

    **Возвращаемый результат**:  
        - Результат в JSON-формате
    """
    r = await get_redis_connection()
    parcel_id = await r.incr("parcel_id")
    parcel_data = parcel.model_dump()
    logger.info({"message": f"Получен запрос на регистарцию посылки с id = {parcel_id}"})
    if not await ParcelsTypeDao.find_one_or_none(id=parcel.type_id):
        await r.decr("parcel_id")
        logger.info({"message": f"Запрос на регистрацию не прошел. Тип посылки с id = {parcel.type_id} не найден"})
        raise HTTPException(
            status_code=400,
            detail={"message": f"Тип посылки с ID {parcel.type_id} не существует в базе данных."}
        )
    post_parcel.delay(parcel_data, parcel_id)
    await post_session(parcel_id, response, request)
    await r.close()
    logger.info({"message": "Послыка с id = {parcel_id} успешно зарегистрирована"})
    return {"id": parcel_id}


@router.get("/{parcel_id}")
async def get_parsels_id(parcel_id: int,
                         parcels_id: list[int] = Depends(get_session)
                         ) -> Union[SParcels, SMessage]:
    """Получение послыки по id.

    **Аргументы**:  
        - parcel_id (int): Id посылки

    **Возвращаемый результат**:  
        - Результат в JSON-формате
    """

    logger.info({"message": f"Запрос на получение посылки с ID {parcel_id}."})
    if parcel_id in parcels_id:
        logger.info({"message": f"Посылка с ID {parcel_id} найдена у данного пользователя."})
        parcel = await ParcelsDao.find_by_id(model_id=parcel_id)
        return create_sparcel(parcel)
    else:
        logger.info(f"Посылка с ID {parcel_id} не найдена у данного.")
        return {
            "message": f"Посылка с id = {parcel_id} отправлена другим пользователем"
        }
