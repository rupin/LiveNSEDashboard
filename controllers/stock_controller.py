from flask import Blueprint, render_template
from models.stock import Stock
from models.market import Market
import plotly.graph_objs as go
import json
from plotly.utils import PlotlyJSONEncoder
import sys, os



stockObjects=[]
stocks_ohlc_data={}

stock_blueprint = Blueprint('stock', __name__)

    
@stock_blueprint.route('/stock/<symbol>/live')
def fetchLive(symbol):
    
    for stockobject in stockObjects:
        if stockobject.getSymbol()==symbol:
            #print(symbol, file=sys.stdout)
            return stockobject.fetch_ohlc_data()       
    
    return Stock.ohlc

           



@stock_blueprint.route('/')
def index():
    # Open the file in read mode
    #print(os.getcwd(), file=sys.stdout)
    filename="list.txt"

    fullpath=os.path.join(os.getcwd(), 'controllers', filename)
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
        ohlc=stockObject.fetch_ohlc_data(preload=True)
        #historicData=stockObject.fetchHistoricData()
        stocks_ohlc_data[symbol]=ohlc
        htmldata={}
        htmldata["stocks_data"]=stocks_ohlc_data
        htmldata["stocks_list"]=stock_list
    #stockObjects=[Stock(symbol) for symbol in stock_list]
    #stocks_data = {stock.getSymbol(): stock.fetch_ohlc_data() for stock in stockObjects}
    return render_template('indexnew.html', html_data=htmldata)


@stock_blueprint.route("/movers")
def movers():
    #print(os.getcwd(), file=sys.stdout)
    mkt=Market()
    mkt.fetchMovers()
    return "Hello"

    


@stock_blueprint.route('/stock/<symbol>')
def stock_data(symbol):
    stock = Stock(symbol)    
    ohlc = stock.fetch_ohlc_data()
    #stock.fetch_rsi()
    history=stock.fetch_history()

    print(history, file=sys.stdout)


    fig = go.Figure(data=[go.Scatter(x=history.index, y=history['close'], mode='lines', name=symbol)])
    graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)

    rsi_fig = go.Figure(data=[go.Scatter(x=history.index, y=history["RSI"], mode='lines', name='RSI')])
    rsi_line = go.Scatter(
            x=history.index,
            y=history["RSI"],
            mode='lines',
            name='RSI',
            line=dict(color='blue')
        )

    layout = go.Layout(
            title='RSI',
            yaxis=dict(
                title='RSI',
                range=[0, 100],
                showgrid=True,
                gridcolor='lightgrey'
            ),
            shapes=[
                dict(
                    type='line',
                    x0=history.index[0],
                    y0=30,
                    x1=history.index[-1],
                    y1=30,
                    line=dict(
                        color='red',
                        width=2,
                        dash='dot'
                    )
                ),
                dict(
                    type='line',
                    x0=history.index[0],
                    y0=70,
                    x1=history.index[-1],
                    y1=70,
                    line=dict(
                        color='green',
                        width=2,
                        dash='dot'
                    )
                )
            ]
        )

    rsi_fig = go.Figure(data=[rsi_line], layout=layout)
    rsiJSON = json.dumps(rsi_fig, cls=PlotlyJSONEncoder)
    return render_template('stock.html', symbol=symbol, ohlc=ohlc, graphJSON=graphJSON, rsiJSON=rsiJSON)
