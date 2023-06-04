from ..models import db, Stock, StockPrice, EMA, PriceChange
from sqlalchemy import desc
from datetime import datetime
import requests
import yfinance as yf
from .data_fetching import get_data
import pandas as pd



def fetch_stock_info(tickers):
    stock_info = {}
    for ticker in tickers.split():
        stock = yf.Ticker(ticker)
        stock_info[ticker] = {
            'Name': stock.info.get('longName'),
            'MarketCap': stock.info.get('marketCap'),
        }
    return stock_info

tickers = "AAPL MSFT GOOGL AMZN TSLA"
stock_info = fetch_stock_info(tickers)


   
def get_icons(ticker):
        return  "{}.png".format(ticker)

def populate_stocks_table(df):
    for ticker in df.columns:
        existing_stock = Stock.query.filter_by(symbol=ticker).first()

        if existing_stock:
            continue 
        latest_data = df[ticker].iloc[-1]

        stock = yf.Ticker(ticker)

        new_stock = Stock(
            icon=get_icons(ticker),
            symbol=ticker,
            name=stock.info.get('longName'),
            marketcap=stock.info.get('marketCap'),
        )
        db.session.add(new_stock)
        db.session.commit()

def populate_stock_prices_table(df):
    for ticker in df.columns:
        stock_id = stock_id_from_ticker(ticker)

        for timestamp, price in df[ticker].items():
            existing_stock_price = StockPrice.query.filter_by(
                timestamp=timestamp,
                stock_id=stock_id,
                price=float("{:.2f}".format(price)),
            ).first()

            if existing_stock_price:
                continue 
            new_stock_price = StockPrice(
                timestamp=timestamp,
                stock_id=stock_id,
                price=float("{:.2f}".format(price)),
            )
            db.session.add(new_stock_price)
            db.session.commit()



def stock_id_from_ticker(ticker):
    stock = Stock.query.filter_by(symbol=ticker).first()
    return stock.id if stock else None
def calculate_200_ema(df):
    return df.ewm(span=200, adjust=False).mean().round(2)
def resample_stock_data(df, time_frame):
    df_resampled = df.resample(time_frame).mean()
    return df_resampled



def populate_ema_table(df, period):
    ema = calculate_200_ema(df)
    for ticker in df.columns:
        stock_id = stock_id_from_ticker(ticker)
        latest_ema = ema[ticker].iloc[-1]
        latest_timestamp = df.index[-1]

        existing_ema = EMA.query.filter_by(
            timestamp=latest_timestamp,
            stock_id=stock_id,
            period=period,
            emas=latest_ema,
        ).first()

        if existing_ema:
            continue

        new_ema = EMA(
            stock_id=stock_id,
            timestamp=latest_timestamp,
            period=period,
            emas=latest_ema,
        )
        db.session.add(new_ema)
    db.session.commit()


def populate_price_change_table(df, periods=[1, 4, 12, 24]):
    latest_timestamp = df.index[-1]
    for ticker in df.columns:
        stock_id = stock_id_from_ticker(ticker)
        latest_price = df[ticker].iloc[-1]

        for period in periods:
            old_timestamp = latest_timestamp - pd.DateOffset(hours=period)
            old_price = df[ticker].loc[old_timestamp:latest_timestamp].iloc[0]
            price_diff = ((latest_price - old_price) / old_price) * 100

            existing_price_change = PriceChange.query.filter_by(
                timestamp=latest_timestamp,
                stock_id=stock_id,
                period=str(period) + 'H',
                price_diff = round(((latest_price - old_price) / old_price) * 100, 2)

            ).first()

            if existing_price_change:
                continue

            new_price_change = PriceChange(
                timestamp=latest_timestamp,
                stock_id=stock_id,
                period=str(period) + 'H',
                price_diff = round(((latest_price - old_price) / old_price) * 100, 2)

            )
            db.session.add(new_price_change)
        db.session.commit()

