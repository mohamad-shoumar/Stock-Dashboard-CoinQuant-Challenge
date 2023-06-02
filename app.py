from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from polygon import RESTClient
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
import yfinance as yf
from datetime import datetime

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'  
app.config['APPLICATION_ROOT'] = '/' 
app.config['PREFERRED_URL_SCHEME'] = 'http'

tickers = "AAPL MSFT GOOGL AMZN TSLA"
period = "15d"
interval = '60m'

data = yf.download(tickers=tickers, period=period, interval=interval, auto_adjust=True, prepost=False, threads=True, proxy=None)
print(data.head())  
print(data.columns)
def fetch_stock_info(tickers):
    stock_info = {}

    for ticker in tickers.split():
        stock = yf.Ticker(ticker)
        stock_info[ticker] = {
            'Name': stock.info.get('longName'),
            'MarketCap': stock.info.get('marketCap'),
        }

    return stock_info

stock_info = fetch_stock_info(tickers)
print(stock_info)

price_diffs = {}
ema_periods = [1, 4, 12, 24]
ema_values = {}

for ticker in tickers.split():
    stock_prices = data.xs(ticker, axis=1, level=1)['Close']
    price_diffs[ticker] = {}

    for period in ema_periods:
        # Calculate price differences
        price_diffs[ticker][f'{period}_Hours_Diff'] = stock_prices.pct_change(periods=period) * 100

        # Calculate EMA values
        ema = stock_prices.ewm(span=period, adjust=False).mean()
        ema_values.setdefault(ticker, {})[f'{period}_Hours_EMA'] = ema.iloc[-1]



# Database Models
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(255)) 
    symbol = db.Column(db.String(10))
    name = db.Column(db.String(100))
    marketcap = db.Column(db.Float)
    price_changes = db.relationship('PriceChange', backref='stock', cascade='all, delete-orphan')
    stock_prices = db.relationship('StockPrice', backref='stock', cascade='all, delete-orphan')
    emas = db.relationship('EMA', backref='stock', cascade='all, delete-orphan')

class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    price = db.Column(db.Float)
class PriceChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    timestamp = db.Column(db.DateTime)
    hours_1 = db.Column(db.Float)
    hours_4 = db.Column(db.Float)
    hours_12 = db.Column(db.Float)
    hours_24 = db.Column(db.Float)


class EMA (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    timestamp = db.Column(db.DateTime)
    hours_1 = db.Column(db.Float)
    hours_4 = db.Column(db.Float)
    hours_12 = db.Column(db.Float)
    hours_24 = db.Column(db.Float)


def populate_tables(data, stock_info):
    for timestamp, row in data.iterrows():
        for ticker in tickers.split():
            stock_data = stock_info[ticker]

            stock = Stock.query.filter_by(symbol=ticker).first()
            if not stock:
                stock = Stock(
                    icon='',
                    symbol=ticker,
                    name=stock_data['Name'],
                    marketcap=stock_data['MarketCap']
                )
                db.session.add(stock)

            existing_stock_price = StockPrice.query.filter_by(timestamp=timestamp, stock=stock).first()
            if existing_stock_price:
                existing_stock_price.price = row['Close'][ticker]
            else:
                stock_price = StockPrice(timestamp=timestamp, price=row['Close'][ticker], stock=stock)
                db.session.add(stock_price)

    db.session.commit()

# route 
@app.route('/', methods=['GET', 'POST'])
def index():
    populate_tables(data, stock_info)
    return render_template('index.html')




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate_tables(data, stock_info)
        app.run(debug=True)