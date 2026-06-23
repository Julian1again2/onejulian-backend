from fastapi import FastAPI

from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.clients import router as clients_router
from app.routers.deliveries import router as deliveries_router
import app.models


Base.metadata.create_all(bind=engine)

app = FastAPI(title="ONEJULIAN Client Portal API")


@app.get("/")
def read_root():
    return {"message": "ONEJULIAN Client Portal API"}


app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(deliveries_router)
