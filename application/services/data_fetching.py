import requests
import yfinance as yf


def get_data():
    tickers = "AAPL MSFT GOOGL AMZN TSLA"
    period = "2y"
    interval = '1h'
    data = yf.download(tickers=tickers, period=period, interval=interval, auto_adjust=True, prepost=False, threads=True, proxy=None)
    df  = data['Close'][tickers.split()]
    return df
