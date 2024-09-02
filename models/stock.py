import os
import pandas as pd
import pandas_ta as ta
from nsepython import *
from datetime import datetime, timedelta

class Stock:
    ohlc={'open': 0,'high':0,'low': 0,'close':0,'ltp':0}
    def __init__(self, symbol):
        self.symbol = symbol
        self.data_dir = 'data'
        self.ohlc=Stock.ohlc
        self.lastrsi=50
        

        self.rename_dict={'CH_TIMESTAMP':'timestamp',
                        'CH_TRADE_HIGH_PRICE':'high',
                        'CH_TRADE_LOW_PRICE':'low',
                        'CH_OPENING_PRICE':'open',
                        'CH_CLOSING_PRICE':'close', 
                        'CH_LAST_TRADED_PRICE':'ltp',
                        'CH_PREVIOUS_CLS_PRICE':'prevclose', 
                        'CH_TOT_TRADED_QTY':'volume',
                        'CH_52WEEK_HIGH_PRICE':'h52w', 
                        'CH_52WEEK_LOW_PRICE':'l52w',
                        'CH_CLOSING_PRICE':'close' }
        self.data_file = os.path.join(self.data_dir, f'{self.symbol}.csv')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def getSymbol(self):
        return self.symbol
    

    

    def fetch_ohlc_data(self, preload=False):       
        if(not preload):
            try:
                data=nse_eq(self.symbol)
                #print(data, file=sys.stdout)

                self.ohlc = {
                    'open': data['priceInfo']['open'],
                    'high': data['priceInfo']['intraDayHighLow']['max'],
                    'low': data['priceInfo']['intraDayHighLow']['min'],
                    'close': data['priceInfo']['previousClose'],
                    'ltp':data['priceInfo']['lastPrice'],
                    'rsi':self.lastrsi
                }
            except Exception as e: 
                print(e)
                
        #print(self.ohlc, file=sys.stdout)
        return self.ohlc
    
    def fetchHistoricData(self):
         # Fetch the last 1 month of data
            end_date =datetime.now().strftime("%d-%m-%Y")
            end_date = str(end_date)

            start_date = (datetime.now()- timedelta(days=30)).strftime("%d-%m-%Y")
            start_date = str(start_date)

            
            series = "EQ"
            history = equity_history(self.symbol,series,start_date,end_date)
            history=history.drop(columns=['_id','TIMESTAMP', 'CH_SYMBOL', 'CH_SERIES', 'CH_MARKET_TYPE', 'CH_TOTAL_TRADES','CH_ISIN','createdAt','updatedAt','__v','SLBMH_TOT_VAL','mTIMESTAMP'])
            history=history.rename(columns=self.rename_dict)

            return history


    def fetch_and_cache_data(self):
        """Fetches stock data and caches it in a CSV file."""
        update_needed = True

        if os.path.exists(self.data_file):
            # Get the last modified date of the CSV file
            last_modified_date = datetime.fromtimestamp(os.path.getmtime(self.data_file)).date()
            today = datetime.now().date()

            # Check if the file was updated today
            if last_modified_date == today:
                update_needed = False


        if update_needed:
           
            #print(history)
            history=self.fetchHistoricData()
            history.to_csv(self.data_file, index=False)
            history = pd.read_csv(self.data_file, index_col='timestamp', parse_dates=True)
            #history.set_index('timestamp')
       
            # Load from cache
        history = pd.read_csv(self.data_file, index_col='timestamp', parse_dates=True)
        history['RSI'] = ta.rsi(history['close'], length=14)
            #last_row_date = history.index[-1]['timestamp']
            
        return history

    def fetch_history(self):
        """Loads historical data from the cached CSV file."""
        return self.fetch_and_cache_data()

    def fetch_rsi(self):
        
        history = self.fetch_history()        
        history['RSI'] = ta.rsi(history['close'], length=14)
        return 
    
    def fetchMovers(self):    
        gainers,movers=nse_preopen_movers("NIFTY")
        print(gainers)

        print(movers)
