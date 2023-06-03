from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
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
period = "2mo"
interval = '1h'

data = yf.download(tickers=tickers, period=period, interval=interval, auto_adjust=True, prepost=False, threads=True, proxy=None)

df  = data['Close'][tickers.split()]
print(df)

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
    period = db.Column(db.Integer)
    price_change = db.Column(db.Float)
 


class EMA (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    timestamp = db.Column(db.DateTime)
    period = db.Column(db.Integer)
    ema = db.Column(db.Float)
   

price_diffs = {}
time_frames = [1, 4, 12, 24]
ema_values = {}

for ticker in tickers.split():
    stock_prices = df[ticker]
    price_diffs[ticker] = {}

    for period in time_frames:
        price_diff = stock_prices.pct_change(periods=period) * 100
        price_diffs[ticker][f'{period}_Hours_Diff'] = price_diff.dropna().tolist()
        ema = stock_prices.rolling(window=200).mean()
        ema_values.setdefault(ticker, {})[f'{period}_Hours_200EMA'] = ema.dropna().tolist()






# route 
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html',df=df)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate_stock_prices_table(df)
        populate_stocks_table(df)
        populate_price_changes_table(price_diff_df)
        populate_emas_table(ema_df)
        app.run(debug=True)
   