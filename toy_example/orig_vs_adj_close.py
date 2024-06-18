from finlab import data
import matplotlib.pyplot as plt

# 取得原始收盤價和還原權值後的收盤價資料
close = data.get("price:收盤價")
adj_close = data.get('etl:adj_close')

# 選擇特定股票，例如台積電 (stock_id = 2330)
stock_id = '2330'
stock_close = close[stock_id]
stock_adj_close = adj_close[stock_id]

# 顯示特定股票的原始和還原權值後的收盤價資料
print(f"Original Close Price for {stock_id}:\n", stock_close.tail())
print(f"Adjusted Close Price for {stock_id}:\n", stock_adj_close.tail())

# 繪製原始和還原權值後的股價走勢圖
plt.figure(figsize=(12, 6))
plt.plot(stock_close, label='Original Close Price')
plt.plot(stock_adj_close, label='Adjusted Close Price', linestyle='--')
plt.title(f"Comparison of Original and Adjusted Close Prices for {stock_id}")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()
