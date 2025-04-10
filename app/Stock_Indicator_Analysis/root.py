# app/Stock_Indicator_Analysis/root.py
from fastapi import APIRouter, HTTPException,Header
from pydantic import BaseModel
import pandas as pd
import requests
from io import BytesIO
from .utils import fetch_indicators, generate_recommendations
from app.common.credit_utils import check_and_deduct_credit

router = APIRouter()

class AnalysisRequest(BaseModel):
    sheet_name: str

@router.post("/stock-indicator-analysis")
def analyze_sheet(request: AnalysisRequest,user_id: str = Header(..., alias="userId")):
    STOCKLIST_URL = "https://github.com/PyStatIQ-Lab/Pystatiq-Stocks-call-generator/raw/main/stocklist.xlsx"
    try:
        
        response = requests.get(STOCKLIST_URL)
        response.raise_for_status()
        xls = pd.ExcelFile(BytesIO(response.content))
        

        if request.sheet_name not in xls.sheet_names:
            raise HTTPException(status_code=400, detail=f"Sheet '{request.sheet_name}' not found in stocklist.xlsx")

        stock_df = pd.read_excel(xls, sheet_name=request.sheet_name)

        if stock_df.empty or 'Symbol' not in stock_df.columns:
            raise HTTPException(status_code=400, detail="The selected sheet does not contain a valid 'Symbol' column.")

        stock_symbols = [sheet_name if '.NS' in sheet_name else f"{sheet_name}.NS" for sheet_name in stock_df['Symbol'].tolist()]

        indicators_list = {}
        for stock in stock_symbols:
            try:
                indicators = fetch_indicators(stock)
                indicators_list[stock] = indicators
            except Exception as e:
                indicators_list[stock] = {"Ticker": stock, "error": str(e)}

        recommendations = generate_recommendations(indicators_list)

        if not isinstance(recommendations, dict) or not all(isinstance(val, list) for val in recommendations.values()):
            raise HTTPException(status_code=400, detail="No valid recommendations generated.")

        result_summary = {}
        for term, stocks in recommendations.items():
            df = pd.DataFrame(stocks)
            if not df.empty:
                # Round numerical columns
                numeric_cols = df.select_dtypes(include=['float64', 'int']).columns
                df[numeric_cols] = df[numeric_cols].round(2)

                # Format percentages
                percent_cols = ['RSI', 'Volatility', 'Strength_Percentage', 'Bullish_Percentage', 
                                'Bearish_Percentage', 'Dividend_Payout_Ratio', 'Promoter_Holding']
                for col in percent_cols:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: f"{x}%" if isinstance(x, (int, float)) else x)

                # Fill missing values
                for col in df.columns:
                    if df[col].isnull().any():
                        df[col] = df[col].fillna('N/A')

                result_summary[term] = df.to_dict(orient="records")
            else:
                result_summary[term] = []

        check_and_deduct_credit(user_id=user_id, model_name="stock_indicator_analysis", required_credits=len(stock_symbols), description="Used stock inndicator analysis prediction model")
        
        return result_summary
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))