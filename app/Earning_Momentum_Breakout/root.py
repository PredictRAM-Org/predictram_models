from fastapi import APIRouter, HTTPException,Header
from pydantic import BaseModel
from typing import Literal
from .utils import load_stocklist, get_stock_data, calculate_stock_scores
import pandas as pd
from app.common.credit_utils import check_and_deduct_credit

router = APIRouter()

class EarningsStrategyRequest(BaseModel):
    sheet_name: str
    risk_tolerance: Literal["Conservative", "Balanced", "Aggressive"] = "Balanced"
    time_horizon: Literal["Hold until Earnings", "Hold 3M Post-Earnings"] = "Hold until Earnings"

@router.post("/earnings-momentum/")
def earnings_momentum_strategy(request: EarningsStrategyRequest,user_id: str = Header(..., alias="userId")):
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

        filtered_df = calculate_stock_scores(stock_df, request.risk_tolerance)
        filtered_df["Entry Point"] = "Buy now (pre-earnings)"
        filtered_df["Exit Point"] = (
            "Sell after earnings" if request.time_horizon == "Hold until Earnings" else "Hold 3 months"
        )

        check_and_deduct_credit(user_id=user_id, model_name="earnings_strategy_model", required_credits=len(symbols), description="Used earnings strategy model")

        return {
            "pre_earnings_picks": filtered_df[["Symbol", "Next Earnings Date", "Breakout Probability %", "Position Size"]].head(10).to_dict(orient="records"),
            "entry_exit_plan": filtered_df[["Symbol", "Breakout Probability %", "Entry Point", "Exit Point"]].head(10).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
