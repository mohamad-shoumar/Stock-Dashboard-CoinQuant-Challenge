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