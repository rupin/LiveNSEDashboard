import argparse
from pathlib import Path
import pandas as pd

import concurrent.futures

import re
from models.stock import Stock

from models.market import Market

def removenonascii(filecontent):    
    result = re.sub(r'[^\x00-\x7f]',r'', filecontent)
    return result

def cleanupCSVFile(filecontents):

    #replace all "," with #

    filecontents=filecontents.replace('","',"#")
    filecontents=filecontents.replace(',',"")
    filecontents=filecontents.replace('#',",")
    filecontents=filecontents.replace('"\n',"#")
    filecontents=filecontents.replace('\n',"")
    filecontents=filecontents.replace('#',"\n")
    filecontents=filecontents.replace('"',"")
    filecontents=filecontents.replace(' ',"")
    filecontents=removenonascii(filecontents)   

    return filecontents


def createStockSymbol(symbol):
    return Stock(symbol)

parser = argparse.ArgumentParser("script")
parser.add_argument("csv", help="A CSV file to process", type=str)
args = parser.parse_args()
filename=args.csv

my_file = Path(filename)

if not my_file.exists():
    print("file not found")
    exit()

""" with open(filename, "r+") as textfile:
    filecontents=cleanupCSVFile(textfile.read())
    #print(filecontents)


newfilename="cleanedup.csv"



# open the file using write only mode
handle = open(newfilename, "w")

# seek out the line you want to overwrite
handle.seek(0)
handle.write(filecontents)
handle.truncate()     
 """

stocks_data=pd.read_csv(filename)
#print(stocks_data)
stocks_data=stocks_data.drop_duplicates(subset=['SYMBOL'])
stocks_data.sort_values(["SYMBOL"], ascending=True, inplace=False)

symbols=stocks_data["SYMBOL"]
stocks_data["stock_object"]=stocks_data["SYMBOL"].apply(lambda symbol:createStockSymbol(symbol))


# Function to call calculate_parameters on a stock object
def process_stock(stockobj):
    
    stockobj.setRefreshFlag(False)
    stockobj.calculate_parameters()

# Create a ThreadPoolExecutor and process in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Pass stock_object column to executor for parallel execution
    futures = {executor.submit(process_stock, stockobj): stockobj for stockobj in stocks_data["stock_object"]}
    
    # Optionally handle the results as they are completed
    for future in concurrent.futures.as_completed(futures):
        stockobj = futures[future]
        try:
            future.result()  # If you want to check for any exceptions
        except Exception as e:
            print(f"An error occurred while processing {stockobj}: {e}")


#stocks_data["stock_object"].apply(lambda stockobj:stockobj.setRefreshFlag(True))
#stocks_data["stock_object"].apply(lambda stockobj:stockobj.calculate_parameters())
market=Market()
market.selectStocks()




#print(stocks_data)
#find stocks which have a very high diifference between low and high.
#stocks_data["volatilitypercent"]=(stocks_
# data["HIGH"]-stocks_data["LOW"])*100/stocks_data["LOW"]

#find stocks which closed very close to the high.
#stocks_data["strength"]=(stocks_data["HIGH"]-stocks_data["LTP"])*100/stocks_data["LTP"]

#stocks_data.to_csv("filteredlist.csv", index=False)
#because of our purchase limits, we cant buy stocks whose ltp is greater than 5000
#stocks_data = stocks_data[stocks_data['LTP'] < 5000]
#filter stocks where the strength is less than 1. 
#stocks_data = stocks_data[stocks_data['strength'] < 1]
#filter stocks where the volatility is greater than 4% 
#stocks_data = stocks_data[stocks_data['volatilitypercent'] > 4]
#print(stocks_data)


#stocks_data=stocks_data.sort_values(by=['volatilitypercent'])
#stocks_data.to_csv("filteredlist.csv", index=False)
#topstocks=stocks_data.tail(40)
#topstocks = topstocks["SYMBOL"]

#topstocks.to_csv('chosen.csv', index=False)  






