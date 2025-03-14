from delivery.dao.base import BaseDao
from .models import Parcels, TypeParcels


class ParcelsDao(BaseDao):
    model = Parcels


class ParcelsTypeDao(BaseDao):
    model = TypeParcels
