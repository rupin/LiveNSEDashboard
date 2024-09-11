import os, re
import pandas as pd
import pandas_ta as ta
from nsepython import *
from datetime import datetime, timedelta

class Stock:
    ohlc={'open': 0,'high':0,'low': 0,'close':0,'ltp':0, 'rsi':50}
    pd.options.mode.copy_on_write = True
    lastDF=pd.DataFrame()
    def __init__(self, symbol):
        self.symbol = symbol
        self.data_dir = 'data'
        self.ohlc=Stock.ohlc
        self.lastrsi=-1
        self.refreshFlag=True
        

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
                        'CH_CLOSING_PRICE':'close',
                        'CH_ISIN':'ISIN'}
        self.data_file = os.path.join(self.data_dir, f'{self.symbol}.csv')
        #print(self.data_file)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def getSymbol(self):
        return self.symbol
    
    def setRefreshFlag(self, value):
        self.refreshFlag=value
    

    

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
                    'rsi':round(self.lastrsi,2)
                }
            except Exception as e: 
                print(e)
                
        #print(self.ohlc, file=sys.stdout)
        return self.ohlc
    
    def fetchHistoricData(self, last_modified_date=None):
         # Fetch the last 60 days of data
            end_date =(datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
            end_date = str(end_date)

            #start_date = (datetime.now()- timedelta(days=60)).strftime("%d-%m-%Y")
            if last_modified_date is not None:
                start_date=last_modified_date.strftime("%d-%m-%Y")
            else:
                start_date = (datetime.now()- timedelta(days=90)).strftime("%d-%m-%Y")
            start_date = str(start_date)

            #print(end_date)
            #print(start_date)

            
            series = "EQ"
            history=None
            try:
            
                history = equity_history(re.escape(self.symbol),series,start_date,end_date)   
            except Exception as e:
                print("------------------------------------------------------------")
                print("{}'s equity history could not be downloaded".format(self.symbol))
                print(e)
                print("------------------------------------------------------------")
                pass        
            
            if history is not None:
                if(history.shape[0]>0):
                    uselesscolumns=['_id','TIMESTAMP','CA', 'CH_SYMBOL', 'CH_SERIES', 'CH_MARKET_TYPE', 'CH_TOTAL_TRADES','createdAt','updatedAt','__v','SLBMH_TOT_VAL','mTIMESTAMP']
                    history=history.drop(columns=uselesscolumns, errors='ignore')
                    history=history.rename(columns=self.rename_dict)                
                    history['timestamp'] = pd.to_datetime(history['timestamp'], format='%Y-%m-%d')                
                    history = history.sort_values(by='timestamp')
                    #history.set_index('timestamp')                
                else:
                    history=None
            return history


    def fetch_and_cache_data(self):
        """Fetches stock data and caches it in a CSV file."""
        
        update_needed = True
        history=None
        last_modified_date=None
        file_exists=os.path.exists(self.data_file)
        #file_exists=False

        if not self.refreshFlag:
                # if the refreshflag is set, it means we have to fetch new data from NSE        
            if file_exists:
                # return the file contents as is.                
                    # Get the date of the last row from the csv            
                    history = self.readCSV()
                    history = history.sort_values(by='timestamp')   
                    return history         
            # following statement gets the value of the timestamp of the last row. The timestamp is the index. 
            """ last_timestamp = history.iloc[-1]['timestamp']
            
            last_timestamp=datetime.strptime(last_timestamp, '%Y-%m-%d')          
            today_date = datetime.today().date()
            #last_timestamp = datetime.last_timestamp.date()
            #print(last_timestamp)


            # Check if the last row's date is today
            if last_timestamp == today_date:
                print("File for {} exists, and it is in order with all data needed.".format(self.symbol))
                return history   

            # if the timestamp in the csv file is old.
            # # we just get the incremental history, by passing a timestamp
            # # then combine the incremental data with the historic data. 
            # # and then save it, and return it.  
            if last_timestamp.date() < today_date:
                print("File for {} exists, but its last timestamp is stale.".format(self.symbol))
                if self.refreshFlag:
                    incremental_history=self.fetchHistoricData(last_timestamp.date())

                    inc_last_timestamp = incremental_history.iloc[-1]['timestamp']                        
                    today_date = datetime.today().date()
                    
                    if inc_last_timestamp.date() < today_date:
                        # even in the new incremental data, we get the data for less than today's date
                        # most likely today is a holiday on the market.
                        pass
                return history


            # Check if the last row's date is today
            if last_timestamp == today_date:
                print("File for {} exists, and it is in order with all data needed.".format(self.symbol))
                return history 




                               
                #print(incremental_history)
                history=history.drop(columns=["RSI"], errors='ignore')
                history = pd.concat([history, incremental_history], axis=0, ignore_index=False, sort=False).fillna(0)
                #history.set_index('timestamp')
                #history = history.sort_values(by='timestamp')
                self.savetoCSV(history)
                return history """
            
        # if the file doesnt exist or the refresh flag is set. 
        # we can get the history of the last 60 days, by not passing an argument.
        # 
        #  
        
        if not file_exists or self.refreshFlag:
            print("File for {} does not exist".format(self.symbol))
            history=self.fetchHistoricData(None)
            
            #print(history.tail(3))
            if(history is not None):

                history = history.sort_values(by='timestamp')
                self.savetoCSV(history)
                return history
            
        return None

                      

           
           
        
            
            
            
        
    """  #print(history)

    if update_needed:          
        print("Updated Needed in {} from {}".format(self.symbol, last_modified_date))
        history = pd.read_csv(self.data_file, index_col='timestamp', parse_dates=True)
        
        if history is not None:
        
            history.to_csv(self.data_file, index=False)
            history = pd.read_csv(self.data_file, index_col='timestamp', parse_dates=True)
        

            # Load from cache
            history = pd.read_csv(self.data_file, index_col='timestamp', parse_dates=True)
            history['RSI'] = ta.rsi(history['close'], length=14)
            history.to_csv(self.data_file) """
                   
    
    def savetoCSV(self,historydf, filename=None):
        historydf=historydf.set_index('timestamp')
        #historydf=historydf.sort_values(by='timestamp')
        #historydf=historydf[['timestamp','open', 'high', 'low', 'close','ltp','prevclose','volume','CH_TOT_TRADED_VAL','h52w','l52w','VWAP']]
        if filename is None:
            historydf.to_csv(self.data_file)
        else:
           historydf.to_csv(filename) 

    def readCSV(self):
        #historydf=historydf.set_index('timestamp')
        #historydf=historydf.sort_values(by='timestamp')
        #historydf=historydf[['timestamp','open', 'high', 'low', 'close','ltp','prevclose','volume','CH_TOT_TRADED_VAL','h52w','l52w','VWAP']]
        historydf=pd.read_csv(self.data_file, parse_dates=True, date_format='%Y-%m-%d')
        return historydf

        

    def fetch_history(self):
        """Loads historical data from the cached CSV file."""
        return self.fetch_and_cache_data()
    

    # Function to calculate % day change based on high and low prices
    def calculate_percent_day_change(self,row):
        #print(row)
        open=row["open"]
        close=row['close']
        if open != 0:  # Avoid division by zero
            val=((close - open) / open) * 100
            return val
        else:
            return 0  # Handle zero low value case
        
    # Function closing strength
    def calculate_day_strength(self,row):
        close=row["close"]
        high=row['high']
        
        if close != 0:  # Avoid division by zero
            
            val=((high - close) / close) * 100
            return val
        else:
            return 0  # Handle zero low value case
        
    # Function closing strength
    def calculate_gap_up(self,row):
        open=row["close"]
        previousclose=row['prevclose']
        
        if previousclose != 0:  # Avoid division by zero
            
            val=((open - previousclose) / previousclose) * 100
            return val
        else:
            return 0  # Handle zero low value case


    def calculate_parameters(self):

        if self.lastrsi<0:
        
            history = self.fetch_history() 
            if history is not None:
                #print(history['high'])
                history['day_rise'] = history.apply(lambda row: self.calculate_percent_day_change(row),axis=1)
                history['strength'] = history.apply(lambda row: self.calculate_day_strength(row),axis=1)  
                history['gapup'] = history.apply(lambda row: self.calculate_gap_up(row),axis=1)  
                          
                history['RSI'] = ta.rsi(history['close'], length=14)     
                
                #history['VWAP_RSI'] = ta.rsi(history['VWAP'], length=14)                
                self.lastrsi=history.tail(1)['RSI'].values[0]
                history['RSI'] = history['RSI'].apply(lambda x: f'{x:.2f}')
                history['strength'] = history['strength'].apply(lambda x: f'{x:.2f}')
                history['day_rise'] = history['day_rise'].apply(lambda x: f'{x:.2f}')
                history['gapup'] = history['gapup'].apply(lambda x: f'{x:.2f}')

                # add MACD Indicators
                macd = ta.macd(history['close'], fast=12, slow=26, signal=9)

                # Append the MACD columns to the DataFrame
                history['macd'] = macd['MACD_12_26_9']     # MACD line
                history['macd_signal'] = macd['MACDs_12_26_9']  # Signal line
                history['macd_hist'] = macd['MACDh_12_26_9']    # MACD Histogram

                history['macd'] = history['macd'].apply(lambda x: f'{x:.2f}')
                history['macd_signal'] = history['macd_signal'].apply(lambda x: f'{x:.2f}')
                history['macd_hist'] = history['macd_hist'].apply(lambda x: f'{x:.2f}')



                last_row=history.tail(1)
                last_row["stock_name"]=self.symbol
                if Stock.lastDF is None:
                    Stock.lastDF = last_row
                else:
                    Stock.lastDF = pd.concat([Stock.lastDF, last_row], axis=0, ignore_index=False, sort=False).fillna(0)
                    #print(Stock.lastDF)
                    self.savetoCSV(Stock.lastDF, "daylist.csv")
                
                self.savetoCSV(history)


    
            
            
    """ def appendLastData(self):
        
        historicData=self.fetch_history()
        
        if(historicData is not None):
            #historicData.to_csv(self.data_file)
        
            #historicData = pd.read_csv(self.data_file, index_col='timestamp', parse_dates=True)

        
            # Access the index (timestamp column)
            last_timestamp = historicData.index[-1]

            # Check if the last row's date is today
            today_date = datetime.today().date()
            if last_timestamp.date() == today_date:
                #Do Nothing
                pass           
                
            else:              
                print(self.symbol)             
                ohlc=self.fetch_ohlc_data(preload=False)
                newData={}
                newData["timestamp"]=pd.Timestamp.today().normalize()
                newData["high"]=ohlc["high"]
                newData["low"]=ohlc["low"]

                newData["open"]=ohlc["open"]
                newData["close"]=ohlc["ltp"]
                newData["prevclose"]=ohlc["close"]
                newData["volume"]=0
                newData["CH_TOT_TRADED_VAL"]=0
                newData["h52w"]=0
                newData["l52w"]=0
                newData["VWAP"]=0                

            

                # Append the new row
                historicData.loc[len(historicData)] = newData
                historicData.to_csv(self.data_file)
                #historicData['timestamp'] = pd.to_datetime(historicData['timestamp'], format='%Y-%m-%d')
            
            #print(historicData) """

    """ def updateHistoryWithToday(self):
         #self.appendLastData()
         self.calculate_rsi() """

               
    
    def fetchMovers(self):    
        gainers,movers=nse_preopen_movers("NIFTY")
        print(gainers)
        print(movers)


""" if __name__ == '__main__':

    filename="list.txt"
    stockObjects=[]
    fullpath=os.path.join(os.getcwd(), filename)
    with open(fullpath, 'r') as file:
    # Read lines, strip newline characters, and add to a list
        stock_list = [line.strip() for line in file]
        stock_list=list(set(stock_list))
        stock_list.sort()
        print(stock_list, file=sys.stdout)
    #stock_list = ['RELIANCE', 'MAZDOCK', 'KTKBANK', 'PCBL', 'JUBLINGREA']
    for symbol in stock_list:
        stockObject=Stock(symbol)
        stockObjects.append(stockObject)
        #print("fetching data for {}".format(symbol), file=sys.stdout)
        
        #print(ohlc)
        
        try:
            pass
            #print("Historic data for {}".format(symbol), file=sys.stdout)
            #print(historicData, file=sys.stdout)
        except Exception as e:
            print(e) """


