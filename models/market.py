import os, sys
import pandas as pd
import pandas_ta as ta
from nsepython import *
from datetime import datetime, timedelta

class Market:
    def __init__(self):
        self.dayList=None
       
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
        

    
    
    def fetchMovers(self):  

        pass

    def addKitLinkToChart(self,row):

        return "https://kite.zerodha.com/chart/web/tvc/NSE/"+row['stock_name']+"/"+row['ISIN']


    def selectStocks(self):
        self.dayList=self.readCSV()
        #self.dayList = self.dayList[self.dayList['gapup'] < self.dayList['day_rise']]
        self.dayList = self.dayList[self.dayList['high'] < 2000]
        self.dayList = self.dayList[self.dayList['gapup'] > 0]
        #self.dayList = self.dayList[self.dayList['strength'] < 1]
        self.dayList = self.dayList[self.dayList['RSI'] < 60]
        self.dayList = self.dayList[self.dayList['macd_hist'] > 0]
        self.dayList=self.dayList.sort_values(['gapup','macd_hist', 'strength'], ascending=[True, False, True])
        #self.dayList["chart_link"]=self.dayList.apply(lambda row:self.addKitLinkToChart(row))
        self.savetoCSV(self.dayList, 'chosen.csv')


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
        dayList=pd.read_csv("daylist.csv", parse_dates=True, date_format='%Y-%m-%d')
        return dayList  
        
        
        
