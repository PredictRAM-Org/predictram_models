import yfinance as yf
import pandas as pd
from datetime import timedelta

def get_financial_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    result = {'Ticker': ticker}

    try:
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        dividends = stock.dividends
    except Exception as e:
        return {"error": f"Error fetching financial data for {ticker}: {str(e)}"}

    try:
        historical_data = stock.history(period="1d")
        latest_close_price = historical_data['Close'].iloc[-1]
    except Exception:
        latest_close_price = None

    def safe_get(df, field):
        return df.loc[field].dropna().to_dict() if field in df.index else None

    result['Net Income'] = safe_get(income_statement, 'Net Income')
    result['Operating Income'] = safe_get(income_statement, 'Operating Income') or safe_get(income_statement, 'EBIT')

    try:
        if 'Earnings Before Interest and Taxes' in income_statement.index:
            ebit = income_statement.loc['Earnings Before Interest and Taxes'].iloc[-1]
            shares = stock.info.get('sharesOutstanding', None)
            result['EPS'] = ebit / shares if shares else None
        else:
            result['EPS'] = None
    except Exception:
        result['EPS'] = None

    try:
        revenue = income_statement.loc['Total Revenue']
        result['Revenue Growth'] = revenue.pct_change().iloc[-1]
    except Exception:
        result['Revenue Growth'] = None

    result['Retained Earnings'] = safe_get(balance_sheet, 'Retained Earnings')
    result['Cash Reserves'] = safe_get(balance_sheet, 'Cash')

    try:
        if 'Total Debt' in balance_sheet.index and 'Stockholders Equity' in balance_sheet.index:
            total_debt = balance_sheet.loc['Total Debt'].iloc[-1]
            equity = balance_sheet.loc['Stockholders Equity'].iloc[-1]
            result['Debt-to-Equity Ratio'] = total_debt / equity
        else:
            result['Debt-to-Equity Ratio'] = None
    except Exception:
        result['Debt-to-Equity Ratio'] = None

    try:
        if 'Total Assets' in balance_sheet.index and 'Total Liabilities Net Minority Interest' in balance_sheet.index:
            total_assets = balance_sheet.loc['Total Assets'].iloc[-1]
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[-1]
            result['Working Capital'] = total_assets - total_liabilities
        else:
            result['Working Capital'] = None
    except Exception:
        result['Working Capital'] = None

    result['Dividend Payout Ratio'] = stock.info.get('dividendYield', None)
    result['Dividend Yield'] = result['Dividend Payout Ratio']

    result['Free Cash Flow'] = safe_get(cash_flow, 'Free Cash Flow')

    if not dividends.empty:
        result['Dividend Growth Rate'] = dividends.pct_change().mean()
        past_dividends = dividends.tail(10)
        result['Past Dividends'] = past_dividends.tolist()

        try:
            date_diffs = past_dividends.index.to_series().diff().dropna()
            if not date_diffs.empty:
                avg_diff = date_diffs.mean()
                last_dividend_date = past_dividends.index[-1]
                next_dividend_date = last_dividend_date + avg_diff
                result['Next Dividend Date'] = str(next_dividend_date.date())
            else:
                result['Next Dividend Date'] = None
        except Exception:
            result['Next Dividend Date'] = None

        predicted_dividend_amount = past_dividends.iloc[-1]
        result['Predicted Dividend Amount'] = predicted_dividend_amount

        if latest_close_price:
            result['Dividend Percentage'] = (predicted_dividend_amount / latest_close_price) * 100
        else:
            result['Dividend Percentage'] = None
    else:
        result['Dividend Growth Rate'] = None
        result['Past Dividends'] = []
        result['Next Dividend Date'] = None
        result['Predicted Dividend Amount'] = None
        result['Dividend Percentage'] = None

    result['Latest Close Price'] = latest_close_price

    return result
