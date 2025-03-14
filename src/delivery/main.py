from fastapi import FastAPI

from delivery.parcels.rourets import router as router_parcels

app = FastAPI()

app.include_router(router_parcels)
