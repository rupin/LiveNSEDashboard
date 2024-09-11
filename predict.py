import os
import pandas as pd
import pandas_ta as ta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load all CSV files
def load_data(data_folder):
    stock_data = {}
    for file in os.listdir(data_folder):
        if file.endswith('.csv'):
            stock_name = file.split('.')[0]
            file_path = os.path.join(data_folder, file)
            df = pd.read_csv(file_path)
            stock_data[stock_name] = df
    return stock_data

# Feature engineering using pandas_ta
def feature_engineering(df):
    # Ensure the data is sorted by timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # Compute technical indicators using pandas_ta
    df['rsi'] = ta.rsi(df['close'], length=14)  # Relative Strength Index
    df['sma_5'] = ta.sma(df['close'], length=5)  # Simple Moving Average (5)
    df['sma_20'] = ta.sma(df['close'], length=20)  # Simple Moving Average (20)
    df['ema_9'] = ta.ema(df['close'], length=9)  # Exponential Moving Average (9)

    # MACD
    macd = ta.macd(df['close'])
    if macd is not None:
        df['macd'] = macd['MACD_12_26_9'].fillna(0)
        df['macd_signal'] = macd['MACDs_12_26_9'].fillna(0)
        df['macd_hist'] = macd['MACDh_12_26_9'].fillna(0)

    # Bollinger Bands
    bbands = ta.bbands(df['close'], length=20)
    if bbands is not None:
        df['bb_upper'] = bbands['BBU_20_2.0'].fillna(0)
        df['bb_middle'] = bbands['BBM_20_2.0'].fillna(0)
        df['bb_lower'] = bbands['BBL_20_2.0'].fillna(0)

    # ATR (Average True Range)
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14).fillna(0)

    # Price Changes
    df['price_change'] = ((df['close'] - df['prevclose']) / df['prevclose']) * 100

    return df


# Add the target column: 1 if the stock rises by at least 2%, 0 otherwise
def create_target(df):
    df['Next_Day_Close'] = df['close'].shift(-1)
    df['Target'] = ((df['Next_Day_Close'] - df['close']) / df['close']) * 100 >= 2
    df['Target'] = df['Target'].astype(int)
    return df

# Function to predict for each stock
def predict_for_stock(stock_df, model):
    stock_df = feature_engineering(stock_df)
    stock_df = create_target(stock_df)
    
    # Use the last row's features to predict the next day's movement
    last_row = stock_df.iloc[-1:]
    features = ['high', 'low', 'open', 'close', 'volume', 'VWAP', 'rsi', 'sma_5', 'sma_20', 'ema_9', 
                'macd', 'macd_signal', 'macd_hist', 'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'price_change']
    X_last = last_row[features]
    
    # Predict
    prediction = model.predict(X_last)
    return prediction

# Main function to identify stocks that will rise by 2%
def identify_rising_stocks(data_folder):
    stock_data = load_data(data_folder)
    
    # Prepare a list to store all stock data after target creation
    all_stock_data = []

    # Process each stock and create targets before combining data
    for stock_name, stock_df in stock_data.items():
        print(stock_name)
        stock_df = feature_engineering(stock_df)
        stock_df = create_target(stock_df)
        all_stock_data.append(stock_df)
    
    # Combine all stock data into one DataFrame
    all_stock_data = pd.concat(all_stock_data)
    all_stock_data = all_stock_data.dropna(subset=['Target'])  # Drop rows where target is not defined
    
    # Features and labels
    features = ['high', 'low', 'open', 'close', 'volume', 'VWAP', 'rsi', 'sma_5', 'sma_20', 'ema_9', 
                'macd', 'macd_signal', 'macd_hist', 'bb_upper', 'bb_middle', 'bb_lower', 'atr', 'price_change']
    X = all_stock_data[features]
    y = all_stock_data['Target']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy}")
    print(classification_report(y_test, y_pred))
    
    # List to hold stocks predicted to rise
    rising_stocks = []
    
    # Loop through all stocks and predict
    for stock_name, stock_df in stock_data.items():
        prediction = predict_for_stock(stock_df, model)
        if prediction == 1:
            rising_stocks.append(stock_name)
    
    return rising_stocks

# Usage
data_folder = 'data'  # Replace with your actual folder path
rising_stocks = identify_rising_stocks(data_folder)
print("Stocks predicted to rise by 2% tomorrow:", rising_stocks)
