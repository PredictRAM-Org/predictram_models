# app/Stock_Indicator_Analysis/root.py
from fastapi import APIRouter, HTTPException,Header
from pydantic import BaseModel
from typing import Literal
from .utils import load_stocklist, get_stock_data, calculate_scores
import pandas as pd
from app.common.credit_utils import check_and_deduct_credit

router = APIRouter()

class QuantModelRequest(BaseModel):
    sheet_name: str
    risk_tolerance: Literal['Low', 'Medium', 'High'] = 'Medium'
    time_horizon: Literal['Short-Term', 'Long-Term'] = 'Long-Term'

@router.post("/quant-model")
def run_quant_model(request: QuantModelRequest,user_id: str = Header(..., alias="userId")):
    try:
        stocklist = load_stocklist()

        if request.sheet_name not in stocklist:
            raise HTTPException(status_code=404, detail=f"Sheet '{request.sheet_name}' not found in stocklist.")

        symbols = stocklist[request.sheet_name]
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols found in the selected sheet.")

        stock_data = [get_stock_data(symbol) for symbol in symbols]
        stock_df = pd.DataFrame([s for s in stock_data if s])

        if stock_df.empty:
            raise HTTPException(status_code=204, detail="No valid stock data found.")

        ranked_df = calculate_scores(stock_df, request.risk_tolerance, request.time_horizon)
        ranked_df["Weight"] = ranked_df["Final Score"] / ranked_df["Final Score"].sum()
        
        check_and_deduct_credit(user_id=user_id, model_name="multifactor_quant_model", required_credits=len(symbols), description="Used multifactor quant model")

        return {
            "top_ranked_stocks": ranked_df[["Symbol", "Final Score"]].head(10).to_dict(orient="records"),
            "portfolio_weights": ranked_df[["Symbol", "Weight"]].head(10).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
