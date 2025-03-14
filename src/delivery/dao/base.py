from delivery.database import asyncs_session_maker
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from delivery.parcels.models import Parcels


class BaseDao:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with asyncs_session_maker() as session:
            if cls.model == Parcels:
                quary = select(cls.model).options(
                    joinedload(cls.model.type)).filter(
                        cls.model.id == model_id)
            else:
                quary = select(cls.model).filter(
                    cls.model.id == model_id)
            result = await session.execute(quary)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with asyncs_session_maker() as session:
            quary = select(cls.model).filter_by(**filter_by)
            result = await session.execute(quary)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, id_parcel: list[int] = None,
                       type_name: str = None,
                       page: int = None, size: int = None):
        async with asyncs_session_maker() as session:
            if cls.model == Parcels:
                query = select(cls.model).options(
                    joinedload(cls.model.type))
            else:
                query = select(cls.model)
            if id_parcel:
                query = query.where(cls.model.id.in_(id_parcel))
            if type_name:
                query = query.filter(Parcels.type.has(name=type_name))
            result = await session.execute(query)
            parcels = result.scalars().all()

            if page is not None and size is not None:
                offset_min = page * size
                offset_max = (page + 1) * size
                parcels = parcels[offset_min:offset_max]
                response = parcels
                return response
            return parcels

