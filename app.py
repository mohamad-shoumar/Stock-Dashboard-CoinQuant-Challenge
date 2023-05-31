from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from polygon import RESTClient
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
import yfinance as yf

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'  
app.config['APPLICATION_ROOT'] = '/' 
app.config['PREFERRED_URL_SCHEME'] = 'http'

tickers = "AAPL MSFT GOOGL AMZN TSLA"
period = "15d"
interval = '60m'

data = yf.download(tickers=tickers, period=period, interval=interval, group_by='tickers', auto_adjust=True, prepost=False, threads=True, proxy=None)
stocks = data
price_diffs = {} 
for ticker in tickers.split():
    data[f'{ticker}_1_hour_diff'] = data[ticker]['Close'].pct_change(periods=1) * 100
    data[f'{ticker}_4_hours_diff'] = data[ticker]['Close'].pct_change(periods=4) * 100
    data[f'{ticker}_12_hours_diff'] = data[ticker]['Close'].pct_change(periods=12) * 100
    data[f'{ticker}_24_hours_diff'] = data[ticker]['Close'].pct_change(periods=24) * 100
    last_1_hour_diff = data[f'{ticker}_1_hour_diff'].iloc[-1]
    last_4_hours_diff = data[f'{ticker}_4_hours_diff'].iloc[-1]
    last_12_hours_diff = data[f'{ticker}_12_hours_diff'].iloc[-1]
    last_24_hours_diff = data[f'{ticker}_24_hours_diff'].iloc[-1]
    price_diffs[ticker] = {
        '1 Hour Diff': last_1_hour_diff,
        '4 Hours Diff': last_4_hours_diff,
        '12 Hours Diff': last_12_hours_diff,
        '24 Hours Diff': last_24_hours_diff,
       
    }

# for ticker, diffs in price_diffs.items():
#     print(f"\nPrice Percentage Differences for {ticker}:")
#     print("1 Hour Diff:", diffs['1 Hour Diff'])
#     print("4 Hours Diff:", diffs['4 Hours Diff'])
#     print("12 Hours Diff:", diffs['12 Hours Diff'])
#     print("24 Hours Diff:", diffs['24 Hours Diff'])


# Database Models
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    hours_1 = db.Column(db.Float)
    hours_4 = db.Column(db.Float)
    hours_12 = db.Column(db.Float)
    hours_24 = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)


# store price difference and prices in DB
# def store_price_data():
#     with app.app_context():
#         last_1_hour_diff = priceData['1_hour_diff'].iloc[-1]
#         last_4_hours_diff = priceData['4_hours_diff'].iloc[-1]
#         last_12_hours_diff = priceData['12_hours_diff'].iloc[-1]
#         last_24_hours_diff = priceData['24_hours_diff'].iloc[-1]

#         stock_price = StockPrice(timestamp=dt.datetime.now(), price=priceData['close'].iloc[-1], stock_id=1)
#         price_change = PriceChange(
#             change_percent=last_1_hour_diff,
#     hours_1=last_1_hour_diff,
#     hours_4=last_4_hours_diff,
#     hours_12=last_12_hours_diff,
#     hours_24=last_24_hours_diff
#         )
#         db.session.add(stock_price)
#         db.session.add(price_change)
#         db.session.commit()
            

# route 
@app.route('/', methods=['GET', 'POST'])
def index():
    # store_price_data()
    # stocks = Stock.query.first() 
    return render_template('index.html')




if __name__ == '__main__':
    with app.app_context():
        index()
        app.run(debug=True)