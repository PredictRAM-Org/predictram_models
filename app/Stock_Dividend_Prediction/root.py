from fastapi import APIRouter, HTTPException,Header
from pydantic import BaseModel
from typing import List
from .utils import get_financial_data
from app.common.credit_utils import check_and_deduct_credit

router = APIRouter()

class StockRequest(BaseModel):
    symbols: List[str]

@router.post("/stock-dividend-prediction")
async def get_stock_data(request: StockRequest,user_id: str = Header(..., alias="userId")):
    try:
        results = []
        for ticker in request.symbols:
            data = get_financial_data(ticker)
            if data is not None:
                results.append(data)
            else:
                results.append({"Ticker": ticker, "error": "Could not retrieve data"})

        check_and_deduct_credit(user_id=user_id, model_name="dividend_predictor", required_credits=len(results), description="Used stock dividend prediction model")

        if  len(results) == 0:
            raise HTTPException(status_code=404, detail="No data found for the given tickers")

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
