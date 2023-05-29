from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
from polygon import RESTClient
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

app = Flask(__name__)


polygon_key = "AWMbFAPJRt11b4FWamJ8lLBNOPgqf8pI"
client = RESTClient(polygon_key)
stockTicker = "AAPL"
from_date = "2023-05-01"
to_date = "2023-05-03"
dataRequest = client.get_aggs(stockTicker, 1, "hour", from_date, to_date)
print (dataRequest)
# BASE_URL = "https://api.polygon.io/v2"
# symbol_list = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
# timeframe = "hour"
# api_url = f"{BASE_URL}/aggs/grouped/locale/us/market/stocks/tickers/{','.join(symbol_list)}/prev?apiKey=AWMbFAPJRt11b4FWamJ8lLBNOPgqf8pI&unadjusted=true&limit=5000&sort=asc&apiKey=AWMbFAPJRt11b4FWamJ8lLBNOPgqf8pI"








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

class PriceChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    change_percent = db.Column(db.Float)
    hours_1 = db.Column(db.Float)
    hours_4 = db.Column(db.Float)
    hours_12 = db.Column(db.Float)
    hours_24 = db.Column(db.Float)

class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    price = db.Column(db.Float)

class EMA (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    hours_1 = db.Column(db.Float)
    hours_4 = db.Column(db.Float)
    hours_12 = db.Column(db.Float)
    hours_24 = db.Column(db.Float)
    value = db.Column(db.Float)

    

@app.route('/', methods=['GET', 'POST'])
def index():
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        results = data["results"]
        stock_data = [result['T'] for result in results]
    else:
        print("Error occurred while fetching data:", response.status_code)
        stock_data = []

    return render_template('index.html', stock_data=stock_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
