import yfinance as yf


def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    result = {'Ticker': ticker}

    try:
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        dividends = stock.dividends
    except Exception as e:
        return {"error": f"Error fetching financial data for {ticker}: {e}"}

    try:
        historical_data = stock.history(period="1d")
        latest_close_price = historical_data['Close'].iloc[-1]
    except Exception:
        latest_close_price = "N/A"

    result['Net Income'] = income_statement.loc['Net Income'] if 'Net Income' in income_statement.index else "N/A"
    result['Operating Income'] = income_statement.loc['Operating Income'] if 'Operating Income' in income_statement.index else \
                                 income_statement.loc['EBIT'] if 'EBIT' in income_statement.index else "N/A"

    try:
        eps = income_statement.loc['Earnings Before Interest and Taxes'] / stock.info['sharesOutstanding']
    except KeyError:
        eps = "N/A"
    result['EPS'] = eps

    result['Revenue Growth'] = income_statement.loc['Total Revenue'].pct_change().iloc[-1] if 'Total Revenue' in income_statement.index else "N/A"
    result['Retained Earnings'] = balance_sheet.loc['Retained Earnings'] if 'Retained Earnings' in balance_sheet.index else "N/A"
    result['Cash Reserves'] = balance_sheet.loc['Cash'] if 'Cash' in balance_sheet.index else "N/A"

    try:
        result['Debt-to-Equity Ratio'] = balance_sheet.loc['Total Debt'] / balance_sheet.loc['Stockholders Equity'] if 'Total Debt' in balance_sheet.index and 'Stockholders Equity' in balance_sheet.index else "N/A"
    except KeyError:
        result['Debt-to-Equity Ratio'] = "N/A"

    result['Working Capital'] = balance_sheet.loc['Total Assets'] - balance_sheet.loc['Total Liabilities Net Minority Interest'] if 'Total Assets' in balance_sheet.index and 'Total Liabilities Net Minority Interest' in balance_sheet.index else "N/A"

    result['Dividend Payout Ratio'] = stock.info.get('dividendYield', "N/A")
    result['Dividend Yield'] = result['Dividend Payout Ratio']

    result['Free Cash Flow'] = cash_flow.loc['Free Cash Flow'] if 'Free Cash Flow' in cash_flow.index else "N/A"

    if not dividends.empty:
        result['Dividend Growth Rate'] = dividends.pct_change().mean()
    else:
        result['Dividend Growth Rate'] = "N/A"

    result['Latest Close Price'] = latest_close_price
    result['Dividend Percentage'] = "N/A"

    if not dividends.empty:
        predicted_dividend_amount = dividends.iloc[-1]
        if latest_close_price != "N/A":
            dividend_percentage = (predicted_dividend_amount / latest_close_price) * 100
            result['Dividend Percentage'] = dividend_percentage

        past_dividends = dividends.tail(10)
        result['Past Dividends'] = past_dividends.tolist()

        date_diffs = past_dividends.index.to_series().diff().dropna()
        if not date_diffs.empty:
            avg_diff = date_diffs.mean()
            last_dividend_date = past_dividends.index[-1]
            next_dividend_date = last_dividend_date + avg_diff
            result['Next Dividend Date'] = str(next_dividend_date)
        else:
            result['Next Dividend Date'] = 'N/A'

        result['Predicted Dividend Amount'] = predicted_dividend_amount
    else:
        result['Next Dividend Date'] = 'N/A'
        result['Predicted Dividend Amount'] = 'N/A'
        result['Dividend Percentage'] = "N/A"

    return result