# app/main.py
from fastapi import FastAPI
from app.PredictRAM_Valuation_Predictor import root as valuation_predictor_router
from app.Stock_Dividend_Prediction import root as dividend_predictor_router
from app.Stock_Indicator_Analysis import root as stock_indicator_analysis_router
from app.Multi_Factor_Quant_Model import root as multi_factor_quant_router
from app.Earning_Momentum_Breakout import root as earning_momentum_router
# from SomeOtherModule import root as other_router

app = FastAPI(title="Predictram models")

# Include app-specific routers
app.include_router(valuation_predictor_router.router)
app.include_router(dividend_predictor_router.router)
app.include_router(stock_indicator_analysis_router.router)
app.include_router(multi_factor_quant_router.router)
app.include_router(earning_momentum_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to the predictram models API!"}
