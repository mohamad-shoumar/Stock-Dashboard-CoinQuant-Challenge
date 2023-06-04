from flask import Blueprint, render_template
from .models import Stock, StockPrice, EMA, PriceChange

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    stocks = Stock.query.all()
    return render_template('index.html', stocks=stocks)
