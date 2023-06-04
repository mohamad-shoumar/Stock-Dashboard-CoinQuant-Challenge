from application import create_app
from application.services.db_operations import (
    populate_stocks_table,
    populate_stock_prices_table,
    populate_ema_table,
    populate_price_change_table,
    resample_stock_data
)
from application.models import db, Stock,StockPrice,EMA,PriceChange
from application.services.data_fetching import get_data

df = get_data()
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate_stocks_table(df) 
        populate_stock_prices_table(df)
        populate_price_change_table(df, periods=[1, 4, 12, 24])
        for period in ['1H', '4H', '12H', '1D']:
            if period != '1H':
                df_resampled = resample_stock_data(df, period)
            else:
                df_resampled = df
            populate_ema_table(df_resampled, period)  
        app.run(debug=True)
