from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from delivery.database import Base


class TypeParcels(Base):
    __tablename__ = 'type_parcels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)


class Parcels(Base):
    __tablename__ = 'parcels'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("type_parcels.id"))
    parcel_value = Column(Float, nullable=False)
    shipping_cost = Column(Float, nullable=True)
    type = relationship("TypeParcels", backref="parcels")
