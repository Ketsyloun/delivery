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
    weight: float
    type_id: int
    parcel_value: float


def create_sparcel(p):
    return SParcels(
        id=p.id,
        name=p.name,
        weight=p.weight,
        type=p.type.name,
        parcel_value=p.parcel_value,
        shipping_cost=p.shipping_cost
    )
