import pandas as pd
import numpy as np
import yfinance as yf
import requests
from io import BytesIO


def load_stocklist():
    url = "https://github.com/PyStatIQ-Lab/Earnings-Momentum-Breakout-Strategy/raw/main/stocklist.xlsx"
    
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

# Fetch stock data from yfinance and calculate technical indicators
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        earnings = stock.calendar
        
        # Fundamental Factors
        earnings_surprise = info.get('earningsSurprise', np.nan)  # % Earnings Beat
        revenue_growth = info.get('revenueGrowth', np.nan)
        
        # Fetch historical price data (6 months)
        hist = stock.history(period="6mo")
        
        if not hist.empty:
            # Calculate technical indicators manually
            
            # EMA50 (Exponential Moving Average)
            hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
            
            # RSI (Relative Strength Index)
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD (Moving Average Convergence Divergence)
            fast_ema = hist['Close'].ewm(span=12, adjust=False).mean()
            slow_ema = hist['Close'].ewm(span=26, adjust=False).mean()
            hist['MACD'] = fast_ema - slow_ema
            hist['MACD_Signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
            
            # Volume Surge (compared to the 20-day moving average volume)
            hist['Volume Surge'] = hist['Volume'] / hist['Volume'].rolling(20).mean()
            
            # Calculate technical conditions
            price_above_ema = 1 if hist['Close'].iloc[-1] > hist['EMA50'].iloc[-1] else 0
            rsi_positive = 1 if hist['RSI'].iloc[-1] > 50 else 0
            macd_crossover = 1 if hist['MACD'].iloc[-1] > hist['MACD_Signal'].iloc[-1] else 0
            volume_surge = 1 if hist['Volume Surge'].iloc[-1] > 1.5 else 0
        else:
            price_above_ema = rsi_positive = macd_crossover = volume_surge = np.nan

        # Next Earnings Date
        next_earnings_date = earnings.get('Earnings Date', [np.nan])[0]

        return {
            "Symbol": symbol,
            "Earnings Surprise %": earnings_surprise if pd.notna(earnings_surprise) else 0,
            "Revenue Growth": revenue_growth if pd.notna(revenue_growth) else 0,
            "Price > EMA50": price_above_ema,
            "RSI > 50": rsi_positive,
            "MACD Bullish": macd_crossover,
            "Volume Surge": volume_surge,
            "Next Earnings Date": next_earnings_date
        }
    except Exception as e:
        return None

# Rank stocks based on Earnings Momentum & Breakout Strategy
def calculate_stock_scores(df, risk_tolerance):
    df = df.dropna().reset_index(drop=True)
    
    # Assigning Scores
    df["Fundamental Score"] = df["Earnings Surprise %"].rank(ascending=False) + df["Revenue Growth"].rank(ascending=False)
    df["Technical Score"] = df["Price > EMA50"] + df["RSI > 50"] + df["MACD Bullish"] + df["Volume Surge"]

    # Calculate Breakout Probability %
    df["Breakout Probability %"] = ((df["Fundamental Score"] * 0.5) + (df["Technical Score"] * 0.5)) * 10
    
    # Adjusting allocation based on risk tolerance
    if risk_tolerance == "Aggressive":
        df["Position Size"] = df["Fundamental Score"] * 1.2 + df["Technical Score"] * 0.8
    elif risk_tolerance == "Conservative":
        df["Position Size"] = df["Fundamental Score"] * 0.8 + df["Technical Score"] * 1.2
    else:
        df["Position Size"] = df["Fundamental Score"] + df["Technical Score"]

    df = df.sort_values(by="Breakout Probability %", ascending=False)
    
    return df