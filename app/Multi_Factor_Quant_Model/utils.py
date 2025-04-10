import pandas as pd
import numpy as np
import yfinance as yf
import requests
from io import BytesIO


def load_stocklist():
    url = "https://github.com/PyStatIQ-Lab/Multi-Factor-Quant-Model-Smart-Beta-/raw/main/stocklist.xlsx"
    
    try:
        # Download the Excel file from GitHub
        response = requests.get(url)
        response.raise_for_status()
        
        # Load Excel from response content
        xls = pd.ExcelFile(BytesIO(response.content))
        sheets = xls.sheet_names

        # Create a dictionary of sheet -> symbol list
        stocklist = {
            sheet: pd.read_excel(xls, sheet_name=sheet)['Symbol'].dropna().astype(str).tolist()
            for sheet in sheets
        }

        return stocklist

    except Exception as e:
        return {"error": f"Failed to load stocklist: {str(e)}"}

# Fetch fundamental & technical data from yfinance
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Fundamental Factors
        pe_ratio = info.get('trailingPE', np.nan)
        roe = info.get('returnOnEquity', np.nan)
        debt_to_equity = info.get('debtToEquity', np.nan)
        earnings_growth = info.get('earningsGrowth', np.nan)
        
        # Technical Factors
        hist = stock.history(period="6mo")
        if not hist.empty:
            six_month_momentum = (hist['Close'][-1] / hist['Close'][0]) - 1  # % Change
            rsi = 100 - (100 / (1 + (hist['Close'].pct_change().dropna().mean() / hist['Close'].pct_change().dropna().std())))
            volume_surge = hist['Volume'][-1] / hist['Volume'].rolling(20).mean()[-1]
        else:
            six_month_momentum = np.nan
            rsi = np.nan
            volume_surge = np.nan
        
        return {
            "Symbol": symbol,
            "P/E Ratio": pe_ratio,
            "ROE": roe,
            "Debt/Equity": debt_to_equity,
            "Earnings Growth": earnings_growth,
            "6M Momentum": six_month_momentum,
            "RSI": rsi,
            "Volume Surge": volume_surge
        }
    except Exception as e:
        return None

# Score Calculation & Ranking
def calculate_scores(df, risk_tolerance, time_horizon):
    # Normalize & assign weights based on user inputs
    df = df.dropna().reset_index(drop=True)
    
    df["Fundamental Score"] = (df["P/E Ratio"].rank(ascending=False) +
                               df["ROE"].rank(ascending=True) +
                               df["Debt/Equity"].rank(ascending=False) +
                               df["Earnings Growth"].rank(ascending=True))
    
    df["Technical Score"] = (df["6M Momentum"].rank(ascending=True) +
                             df["RSI"].rank(ascending=True) +
                             df["Volume Surge"].rank(ascending=True))
    
    # Adjust weights based on Risk & Time Horizon
    fundamental_weight = 0.7 if time_horizon == "Long-Term" else 0.4
    technical_weight = 0.3 if time_horizon == "Long-Term" else 0.6
    
    if risk_tolerance == "Low":
        fundamental_weight += 0.1
        technical_weight -= 0.1
    elif risk_tolerance == "High":
        fundamental_weight -= 0.1
        technical_weight += 0.1

    df["Final Score"] = df["Fundamental Score"] * fundamental_weight + df["Technical Score"] * technical_weight
    df = df.sort_values(by="Final Score", ascending=False)
    
    return df