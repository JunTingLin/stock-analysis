import pandas as pd
import numpy as np
from finlab import data
from finlab.backtest import sim
from get_data import get_data_from_finlab

# 設定股票宇宙
# with data.universe(market='TSE_OTC', category=['水泥工業']):
# 獲取股價和市值數據
# close = data.get("price:收盤價")
# market_value = data.get("etl:market_value")

close = get_data_from_finlab("price:收盤價", use_cache=True)
market_value = get_data_from_finlab("etl:market_value", use_cache=True)

# 計算條件
ma60 = close.average(60)
ma60_rising = ma60 > ma60.shift(1)
above_ma60 = close > ma60
high_3m = close.rolling(60).max()
price_break_high_3m = close >= high_3m
# market_value_condition = market_value > 15000000000  # 150億台幣

# 買入條件
buy_condition = above_ma60 & ma60_rising & price_break_high_3m

# 賣出條件
below_ma60 = close < ma60
not_recover_in_5_days = below_ma60.sustain(5)
ma60_falling = ma60 < ma60.shift(1)

# 初始化持倉狀態DataFrame
position = pd.DataFrame(data=0, index=close.index, columns=close.columns)  # 將NaN改為初始為0表示無持有

# 遍歷每一天，除了最後一天（因為最後一天無法執行買賣）
for i in range(len(close.index)-1):
    today = close.index[i]
    next_day = close.index[i + 1]  # 獲取下一個交易日
    
    # 繼承昨天的持倉到今天
    if today > position.index[0]:
        position.loc[next_day] = position.loc[today]  # 首先將今天的持倉狀態複製到下一天
    
    # 處理買入訊號，對下一個交易日的持倉進行調整
    if today in buy_condition.index and buy_condition.loc[today].any():
        buy_signals = buy_condition.loc[today]
        position.loc[next_day, buy_signals] = 1  # 在下一個交易日買入

    # 處理賣出訊號，對下一個交易日的持倉進行調整
    # 跌破季線且五日內未能站回，賣出 1/3
    if today in not_recover_in_5_days.index and not_recover_in_5_days.loc[today].any():
        sell_1_3 = not_recover_in_5_days.loc[today] & (position.loc[today] > 0)
        position.loc[next_day, sell_1_3] *= 2/3
    
    # 如果季線開始下彎，全部賣出
    if today in ma60_falling.index and ma60_falling.loc[today].any():
        sell_all = ma60_falling.loc[today] & (position.loc[today] > 0)
        position.loc[next_day, sell_all] = 0


# 進行回測，不指定重採樣參數
report = sim(position, resample=None)
