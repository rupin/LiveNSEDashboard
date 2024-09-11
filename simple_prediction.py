import pandas as pd
import glob

# Define parameters
rsi_threshold = 40
percentage_increase = 3

# Get all CSV files in the folder
csv_files = glob.glob("data/*.csv")

# List to hold potential stocks
potential_stocks = []

# Iterate over each CSV file
for file in csv_files:
    # Load the data
    df = pd.read_csv(file)
    
    # Ensure 'RSI', 'Close', and 'Timestamp' columns exist
    if 'RSI' in df.columns and 'close' in df.columns and 'timestamp' in df.columns:
        # Sort by timestamp if not already sorted
        df = df.sort_values(by='timestamp')
        
        # Find rows where RSI is below the threshold
        oversold = df[df['RSI'] < rsi_threshold]
        
        # Check if next day's price increases by the target percentage
        for i in range(len(oversold) - 1):
            today_close = oversold.iloc[i]['close']
            next_day_close = oversold.iloc[i + 1]['close']
            
            # Calculate percentage increase
            change = ((next_day_close - today_close) / today_close) * 100
            if change >= percentage_increase:
                potential_stocks.append(file)
                break

# Print potential stocks
print('\n'.join(potential_stocks))
#print(f"Stocks with potential rise tomorrow: {potential_stocks}")
