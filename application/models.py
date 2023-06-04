from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    price_diff = db.Column(db.Float)
 


class EMA (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'))
    timestamp = db.Column(db.DateTime)
    period = db.Column(db.Integer)
    emas = db.Column(db.Float)