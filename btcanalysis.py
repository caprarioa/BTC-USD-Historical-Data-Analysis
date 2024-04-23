import pandas as pd
import matplotlib.pyplot as plt
import ta

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

# Plotting MACD
axes[2].plot(df['MACD_line'], label='MACD Line', color='blue')
axes[2].plot(df['Signal_line'], label='Signal Line', color='orange')
axes[2].bar(df.index, df['MACD_line'] - df['Signal_line'], label='MACD Histogram', color='gray', alpha=0.5)
axes[2].legend()
axes[2].set_title('Moving Average Convergence Divergence (MACD)')

# Improve layout and show plot
plt.tight_layout()
plt.show()
