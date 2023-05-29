from flask import Flask, render_template
import requests
app = Flask(__name__)


BASE_URL = "https://api.polygon.io/v2"
symbol_list = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"]
timeframe = "hour"
api_url = f"{BASE_URL}/aggs/grouped/locale/us/market/stocks/tickers/{','.join(symbol_list)}/prev?apiKey=AWMbFAPJRt11b4FWamJ8lLBNOPgqf8pI&unadjusted=true&limit=5000&sort=asc&apiKey=AWMbFAPJRt11b4FWamJ8lLBNOPgqf8pI"

@app.route('/')
def index():
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            results  = data["results"]
            stock_data = [result['T'] for result in results]  
        else:
             print("Error occurred while fetching data:", response.status_code)
             stock_data = []

        return render_template('index.html', stock_data=stock_data)
if __name__ == '__main__':
    app.run()