# app/main.py
from fastapi import FastAPI
from app.PredictRAM_Valuation_Predictor import root as valuation_predictor_router
# from SomeOtherModule import root as other_router

app = FastAPI(title="Predictram models")

# Include app-specific routers
app.include_router(valuation_predictor_router.router)
# app.include_router(other_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to the predictram models API!"}
