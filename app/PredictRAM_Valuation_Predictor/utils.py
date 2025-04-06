import yfinance as yf

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period='1y')
    info = stock.info
    dividend_history = stock.dividends
    shares_outstanding = stock.info.get('sharesOutstanding', 0)

    financials = {
        'P/E Ratio': info.get('trailingPE', 'N/A'),
        'P/B Ratio': info.get('priceToBook', 'N/A'),
        'EV/EBITDA': info.get('enterpriseToEbitda', 'N/A'),
        'ROE (%)': round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 'N/A',
        'Market Cap': info.get('marketCap', 'N/A'),
        'Dividend Yield (%)': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 'N/A',
        'Shares Outstanding': shares_outstanding,
        'P/S Ratio': info.get('priceToSalesTrailing12Months', 'N/A'),
        'P/CF Ratio': info.get('priceToCashflow', 'N/A'),
        'Debt-to-Equity': info.get('debtToEquity', 'N/A'),
        'Beta': info.get('beta', 'N/A'),
        'Earnings Surprise': info.get('earningsQuarterlyGrowth', 'N/A'),
        'Analyst Rating': info.get('recommendationKey', 'N/A'),
        'Quick Ratio': info.get('quickRatio', 'N/A'),
        'Current Ratio': info.get('currentRatio', 'N/A'),
        'EBITDA': info.get('ebitda', 'N/A'),
        'Free Cash Flow': info.get('freeCashflow', 'N/A'),
        'Revenue Growth': info.get('revenueGrowth', 'N/A'),
        'Gross Margins': info.get('grossMargins', 'N/A'),
        'EBITDA Margins': info.get('ebitdaMargins', 'N/A'),
        'Operating Margins': info.get('operatingMargins', 'N/A'),
        'Trailing PEG Ratio': info.get('trailingPegRatio', 'N/A'),
    }
    return hist.to_dict(), financials, dividend_history.to_dict()


def valuation_analysis(financials, stock_choice):
    analysis = []
    pe = financials['P/E Ratio']
    pb = financials['P/B Ratio']
    ev_ebitda = financials['EV/EBITDA']
    debt_to_equity = financials['Debt-to-Equity']
    quick_ratio = financials['Quick Ratio']
    current_ratio = financials['Current Ratio']
    free_cash_flow = financials['Free Cash Flow']

    if pe != 'N/A' and pe < 20:
        analysis.append(f"{stock_choice} appears undervalued based on P/E ratio ({pe}).")
    else:
        analysis.append(f"{stock_choice} might be overvalued based on P/E ratio ({pe}).")

    if pb != 'N/A' and pb < 3:
        analysis.append(f"{stock_choice} appears fairly valued based on P/B ratio ({pb}).")
    else:
        analysis.append(f"{stock_choice} might be overvalued based on P/B ratio ({pb}).")

    if ev_ebitda != 'N/A' and ev_ebitda < 10:
        analysis.append(f"{stock_choice} has a reasonable valuation based on EV/EBITDA ({ev_ebitda}).")
    else:
        analysis.append(f"{stock_choice} might be expensive based on EV/EBITDA ({ev_ebitda}).")

    if debt_to_equity != 'N/A' and debt_to_equity < 1.0:
        analysis.append(f"{stock_choice} has a healthy debt-to-equity ratio ({debt_to_equity}).")
    else:
        analysis.append(f"{stock_choice} has a high debt-to-equity ratio ({debt_to_equity}), indicating higher financial risk.")

    if quick_ratio != 'N/A' and quick_ratio >= 1:
        analysis.append(f"{stock_choice} has a good quick ratio ({quick_ratio}), indicating sufficient liquidity.")
    else:
        analysis.append(f"{stock_choice} might have liquidity issues with a quick ratio of ({quick_ratio}).")

    if current_ratio != 'N/A' and current_ratio >= 1.5:
        analysis.append(f"{stock_choice} has a strong current ratio ({current_ratio}), indicating good short-term financial health.")
    else:
        analysis.append(f"{stock_choice} has a low current ratio ({current_ratio}), which might indicate liquidity concerns.")

    if free_cash_flow != 'N/A' and free_cash_flow > 0:
        analysis.append(f"{stock_choice} has positive free cash flow, which is a good sign for financial health.")
    else:
        analysis.append(f"{stock_choice} has negative or no free cash flow, which might be a red flag.")

    return analysis


def predict_valuation_shift(financials, stock_choice):
    prediction = []
    if financials['P/E Ratio'] != 'N/A' and financials['P/E Ratio'] > 25:
        prediction.append(f"{stock_choice} is currently overvalued based on its P/E ratio.")

        if financials['Debt-to-Equity'] != 'N/A' and financials['Debt-to-Equity'] > 1.0:
            prediction.append(f"{stock_choice} has a high debt-to-equity ratio, indicating higher risk in the future.")

        if financials['P/S Ratio'] != 'N/A' and financials['P/S Ratio'] > 5:
            prediction.append(f"{stock_choice} has a high P/S ratio, further indicating overvaluation.")

        prediction.append(f"{stock_choice} might become undervalued if its valuation metrics return to historical averages.")

    return prediction
