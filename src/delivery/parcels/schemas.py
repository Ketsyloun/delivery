from fastapi import Query
from pydantic import BaseModel


class SParcels(BaseModel):
    id: int
    name: str
    weight: float
    type: str
    parcel_value: float
    shipping_cost: float


class SParcelsPost(BaseModel):
    name: str
    weight: float = Query(ge=0.1)
    type_id: int = Query(ge=1)
    parcel_value: float = Query(ge=0)


def create_sparcel(p):
    return SParcels(
        id=p.id,
        name=p.name,
        weight=p.weight,
        type=p.type.name,
        parcel_value=p.parcel_value,
        shipping_cost=p.shipping_cost
    )
    

class SParcelsType(BaseModel):
    id: int
    name: str
    
class SMessage(BaseModel):
    name: str
