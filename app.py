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


price_diff_df = pd.DataFrame(columns=['Ticker', 'Period', 'Timestamp', 'Value'])
for ticker in price_diffs:
    for period in price_diffs[ticker]:
        for i, value in enumerate(price_diffs[ticker][period]):
            timestamp = df.index[i]  # Assuming timestamps are the indices of your original DataFrame
            price_diff_df = pd.concat([price_diff_df, pd.DataFrame({'Ticker': ticker, 'Period': period, 'Timestamp': timestamp, 'Value': value}, index=[0])], ignore_index=True)

ema_df = pd.DataFrame(columns=['Ticker', 'Period', 'Timestamp', 'Value'])
for ticker in ema_values:
    for period in ema_values[ticker]:
        for i, value in enumerate(ema_values[ticker][period]):
            timestamp = df.index[i]  # Assuming timestamps are the indices of your original DataFrame
            ema_df = pd.concat([ema_df, pd.DataFrame({'Ticker': ticker, 'Period': period, 'Timestamp': timestamp, 'Value': value}, index=[0])], ignore_index=True)


print("price_diffs_df:")
print(price_diff_df)

print("\nema_values_df:")
print(ema_df)

def populate_price_changes_table(price_diff_df):
    for _, row in price_diff_df.iterrows():
        stock_id = stock_id_from_ticker(row['Ticker'])
        existing_price_change = PriceChange.query.filter_by(
            stock_id=stock_id,
            timestamp=row['Timestamp'],
            period=int(row['Period'].split('_')[0])
        ).first()

        if existing_price_change:
            continue
        new_price_change = PriceChange(
            stock_id=stock_id,
            timestamp=row['Timestamp'],
            period=int(row['Period'].split('_')[0]),
            price_change=row['Value'],
        )

        db.session.add(new_price_change)
        db.session.commit()

def populate_emas_table(ema_df):
    for _, row in ema_df.iterrows():
        stock_id = stock_id_from_ticker(row['Ticker'])
        existing_ema = EMA.query.filter_by(
            stock_id=stock_id,
            timestamp=row['Timestamp'],
            period=int(row['Period'].split('_')[0])
        ).first()

        if existing_ema:
            continue
        new_ema = EMA(
            stock_id=stock_id,
            timestamp=row['Timestamp'],
            period=int(row['Period'].split('_')[0]),
            ema=row['Value'],
        )

        db.session.add(new_ema)
        db.session.commit()

def populate_stocks_table(df):
    for ticker in df.columns:
        existing_stock = Stock.query.filter_by(symbol=ticker).first()

        if existing_stock:
            continue 
        latest_data = df[ticker].iloc[-1]

        stock = yf.Ticker(ticker)

        new_stock = Stock(
            icon=None,  
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
                price=price
            ).first()

            if existing_stock_price:
                continue 
            new_stock_price = StockPrice(
                timestamp=timestamp,
                stock_id=stock_id,
                price=price,
            )
            db.session.add(new_stock_price)
            db.session.commit()





def stock_id_from_ticker(ticker):
    stock = Stock.query.filter_by(symbol=ticker).first()
    return stock.id if stock else None





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
   