import pandas as pd
import matplotlib.pyplot as plt
import ta
import yfinance as yf

def update_data(file_path):
    # Load your existing data and clean any empty rows
    df_existing = pd.read_csv(file_path, index_col='Date', parse_dates=True)
    df_existing.dropna(inplace=True)

    # Determine the last date in your dataset
    last_date = df_existing.index.max()

    # Fetch new data from the day after the last date in your dataset to today
    start_date = last_date + pd.Timedelta(days=1)
    df_new = yf.download('BTC-USD', start=start_date, end=pd.Timestamp.today())

    # Ensure no empty data and proper datetime index
    df_new.dropna(inplace=True)
    df_new.index = pd.to_datetime(df_new.index)

    # If there is new data, append it
    if not df_new.empty:
        df_updated = pd.concat([df_existing, df_new[['Open', 'High', 'Low', 'Close', 'Volume']]])
        df_updated.to_csv(file_path)  # Save the updated DataFrame back to CSV
        print("Data updated successfully.")
    else:
        print("No new data available.")

# Usage
file_path = 'BTC-USD.csv'
update_data(file_path)

# Load the data
file_path = 'BTC-USD.csv'
df = pd.read_csv(file_path, usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
                 parse_dates=['Date'], 
                 names=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], 
                 header=0)
df.set_index('Date', inplace=True)

# Calculate Moving Averages for Golden Cross and Death Cross
df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)

# Calculate Bollinger Bands
indicator_bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
df['bb_bbm'] = indicator_bb.bollinger_mavg()  # Middle Bollinger Band (SMA)
df['bb_bbh'] = indicator_bb.bollinger_hband()  # Upper Bollinger Band
df['bb_bbl'] = indicator_bb.bollinger_lband()  # Lower Bollinger Band

# Identify Golden Cross and Death Cross
df['Golden_Cross'] = (df['SMA_50'] > df['SMA_200']) & (df['SMA_50'].shift(1) < df['SMA_200'].shift(1))
df['Death_Cross'] = (df['SMA_50'] < df['SMA_200']) & (df['SMA_50'].shift(1) > df['SMA_200'].shift(1))

# Calculate MACD
macd = ta.trend.MACD(df['Close'])
df['MACD_line'] = macd.macd()
df['Signal_line'] = macd.macd_signal()

# Calculate RSI
df['RSI'] = ta.momentum.rsi(df['Close'])

# Create a figure and a set of subplots
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 10), sharex=True)

# Plotting the closing prices with SMA for Crosses
axes[0].plot(df['Close'], label='Close Price', color='blue', alpha=0.5)
axes[0].plot(df['SMA_50'], label='50-Day SMA', color='red')
axes[0].plot(df['SMA_200'], label='200-Day SMA', color='green')
axes[0].scatter(df.index[df['Golden_Cross']], df['SMA_50'][df['Golden_Cross']], color='gold', marker='^', s=100, label='Golden Cross')
axes[0].scatter(df.index[df['Death_Cross']], df['SMA_50'][df['Death_Cross']], color='black', marker='v', s=100, label='Death Cross')
axes[0].legend()
axes[0].set_title('BTC-USD Price and Moving Averages')

# Plotting RSI
axes[1].plot(df['RSI'], label='RSI', color='purple')
axes[1].axhline(70, linestyle='--', alpha=0.5, color='red')
axes[1].axhline(30, linestyle='--', alpha=0.5, color='green')
axes[1].fill_between(df.index, df['RSI'], 70, where=(df['RSI'] >= 70), facecolor='red', alpha=0.5, interpolate=True)
axes[1].fill_between(df.index, df['RSI'], 30, where=(df['RSI'] <= 30), facecolor='green', alpha=0.5, interpolate=True)
axes[1].set_title('Relative Strength Index (RSI)')
axes[1].legend()



# Plotting the closing prices with SMA and Bollinger Bands
axes[0].fill_between(df.index, df['bb_bbh'], df['bb_bbl'], color='gray', alpha=0.3, label='Bollinger Bands')
axes[0].legend()
axes[0].set_title('BTC-USD Bollinger Bands')



# Plotting MACD
axes[2].plot(df['MACD_line'], label='MACD Line', color='blue')
axes[2].plot(df['Signal_line'], label='Signal Line', color='orange')
axes[2].bar(df.index, df['MACD_line'] - df['Signal_line'], label='MACD Histogram', color='gray', alpha=0.5)
axes[2].legend()
axes[2].set_title('Moving Average Convergence Divergence (MACD)')

# Improve layout and show plot
plt.tight_layout()
plt.show()
