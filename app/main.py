from fastapi import FastAPI

from app.routers import auth, clients, deliveries, payments
from policy_api_router import router as policy_router

app = FastAPI(title="ONEJULIAN Rail API")

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(deliveries.router)
app.include_router(payments.router)
app.include_router(policy_router)

@app.get("/")
def root():
    return {"message": "ONEJULIAN Rail API"}
