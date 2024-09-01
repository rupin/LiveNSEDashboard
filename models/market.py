import os
import pandas as pd
import pandas_ta as ta
from nsepython import *
from datetime import datetime, timedelta

class Market:
    def __init__(self):
       
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
        gainers,losers=nse_preopen_movers("NIFTY")
        gainers["state"]="GAINER"
        losers["state"]="LOSER"
        
