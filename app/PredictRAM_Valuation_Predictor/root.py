# app/PredictRAM-Valuation-Predictor/root.py
from fastapi import APIRouter, HTTPException,Header
from pydantic import BaseModel
from .utils import get_stock_data, valuation_analysis, predict_valuation_shift
from app.common.credit_utils import check_and_deduct_credit

router = APIRouter()

class StockRequest(BaseModel):
    symbol: str

@router.post("/valuation-predictor")
def analyze_stock(request: StockRequest,user_id: str = Header(..., alias="userId")):
    symbol = request.symbol.upper()
    if '.' not in symbol:
        raise HTTPException(status_code=400, detail="Invalid stock symbol format. Include exchange suffix like '.NS'")
    
    try:
        hist, financials, dividends = get_stock_data(symbol)
        valuation = valuation_analysis(financials, symbol)
        prediction = predict_valuation_shift(financials, symbol)

        # Check and deduct credits
        check_and_deduct_credit(user_id=user_id, model_name="valuation_predictor", required_credits=1, description="Used valuation prediction model")


        return {
            "symbol": symbol,
            "financials": financials,
            "valuation_analysis": valuation,
            "valuation_prediction": prediction,
            "price_history": hist,
            "dividends": dividends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
