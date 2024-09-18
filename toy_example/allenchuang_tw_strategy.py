from finlab import data

# 獲取三大法人的買賣超數據
foreign_net_buy = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')
foreign_self_net_buy = data.get('institutional_investors_trading_summary:外資自營商買賣超股數')
investment_trust_net_buy = data.get('institutional_investors_trading_summary:投信買賣超股數')
dealer_self_net_buy = data.get('institutional_investors_trading_summary:自營商買賣超股數(自行買賣)')
dealer_hedge_net_buy = data.get('institutional_investors_trading_summary:自營商買賣超股數(避險)')

# 發行股數作為總股數
shares_outstanding = data.get('internal_equity_changes:發行股數')

# 計算法人買超佔發行量的比例
foreign_total_net_buy = foreign_net_buy + foreign_self_net_buy  # 外資 = 外陸資買賣超 + 外資自營商
foreign_net_buy_ratio = foreign_total_net_buy / shares_outstanding

investment_trust_net_buy_ratio = investment_trust_net_buy / shares_outstanding

dealer_total_net_buy = dealer_self_net_buy + dealer_hedge_net_buy  # 自營商 = 自營商自行買賣 + 避險
dealer_self_net_buy_ratio = dealer_total_net_buy / shares_outstanding

# 計算外資、投信、自營商的3天和5天累積買超比例
foreign_net_buy_3d_sum = foreign_net_buy_ratio.rolling(3).sum()
foreign_net_buy_5d_sum = foreign_net_buy_ratio.rolling(5).sum()

investment_trust_net_buy_3d_sum = investment_trust_net_buy_ratio.rolling(3).sum()
investment_trust_net_buy_5d_sum = investment_trust_net_buy_ratio.rolling(5).sum()

dealer_self_net_buy_3d_sum = dealer_self_net_buy_ratio.rolling(3).sum()
dealer_self_net_buy_5d_sum = dealer_self_net_buy_ratio.rolling(5).sum()

# 設定每個法人的前5檔股票排名
top_n = 5

# 外資：取前3天和5天累積買超比例最大的5檔股票
foreign_3d_top_n = foreign_net_buy_3d_sum.rank(axis=1, ascending=False) <= top_n
foreign_5d_top_n = foreign_net_buy_5d_sum.rank(axis=1, ascending=False) <= top_n
foreign_buy_condition = foreign_3d_top_n | foreign_5d_top_n

# 投信：取前3天和5天累積買超比例最大的5檔股票
investment_trust_3d_top_n = investment_trust_net_buy_3d_sum.rank(axis=1, ascending=False) <= top_n
investment_trust_5d_top_n = investment_trust_net_buy_5d_sum.rank(axis=1, ascending=False) <= top_n
investment_trust_buy_condition = investment_trust_3d_top_n | investment_trust_5d_top_n

# 自營商：取前3天和5天累積買超比例最大的5檔股票
dealer_self_3d_top_n = dealer_self_net_buy_3d_sum.rank(axis=1, ascending=False) <= top_n
dealer_self_5d_top_n = dealer_self_net_buy_5d_sum.rank(axis=1, ascending=False) <= top_n
dealer_self_buy_condition = dealer_self_3d_top_n | dealer_self_5d_top_n


# 獲取每檔股票的收盤價數據
close_price = data.get('price:收盤價')

# 計算每檔股票的買賣超金額
foreign_net_buy_amount = foreign_total_net_buy * close_price  # 外資買賣超金額
investment_trust_net_buy_amount = investment_trust_net_buy * close_price  # 投信買賣超金額
dealer_net_buy_amount = dealer_total_net_buy * close_price  # 自營商買賣超金額
# 總體買賣超金額 = 外資 + 投信 + 自營商的買賣超金額
total_net_buy_amount = foreign_net_buy_amount + investment_trust_net_buy_amount + dealer_net_buy_amount

# 設定每檔股票買賣超金額前3名
top_n = 3
total_market_top_3 = total_net_buy_amount.rank(axis=1, ascending=False) <= top_n

# 最終條件：三大法人的股票聯集
chip_buy_condition = foreign_buy_condition | investment_trust_buy_condition | dealer_self_buy_condition | total_market_top_3

# 獲取收盤價數據
adj_close = data.get('etl:adj_close')

# 計算均線
ma5 = adj_close.rolling(5).mean()
ma10 = adj_close.rolling(10).mean()
ma20 = adj_close.rolling(20).mean()
ma60 = adj_close.rolling(60).mean()

# 均線上升
ma_up_buy_condition = (ma5 > ma5.shift(1)) & (ma10 > ma10.shift(1)) & (ma20 > ma20.shift(1)) & (ma60 > ma60.shift(1))

# 價格在均線之上
price_above_ma_buy_condition = (adj_close > ma5) & (adj_close > ma10) & (adj_close > ma20) & (adj_close > ma60)

# 計算乖離率
bias_10 = (adj_close - ma10) / ma10
bias_20 = (adj_close - ma20) / ma20

# 乖離率小於0.14
bias_buy_condition = (bias_10.abs() < 0.14) & (bias_20.abs() < 0.14)

# 獲取成交量數據
volume = data.get('price:成交股數')

# 成交量大於昨日的2.5倍
volume_buy_condition = volume > (volume.shift(1) * 2.5)

# 計算DMI指標
plus_di = data.indicator('PLUS_DI', timeperiod=14, adjust_price=True)
minus_di = data.indicator('MINUS_DI', timeperiod=14, adjust_price=True)

# DMI條件
dmi_buy_condition = (plus_di > 28) & (minus_di < 20) | (plus_di > 26) & (minus_di < 18)

# 計算 KD 指標
k, d = data.indicator('STOCH', adjust_price=True)

# KD 指標條件：%K 和 %D 都向上
kd_buy_condition = (k > k.shift(1)) & (d > d.shift(1))

# 計算 MACD 指標
macd, signal, hist = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)
dif = macd  # MACD 中的 DIF

# MACD DIF 向上
macd_dif_buy_condition = dif > dif.shift(1)

# 技術面
technical_buy_condition = ma_up_buy_condition & price_above_ma_buy_condition & bias_buy_condition & volume_buy_condition & dmi_buy_condition & kd_buy_condition & macd_dif_buy_condition

# 最終的買入訊號
buy_signal = chip_buy_condition & technical_buy_condition

# ### 新增的賣出條件
# 停損條件：DMI條件
dmi_sell_condition = (plus_di < 35) & (minus_di > 18)

# 停損條件：KD指標 %K 和 %D 都向下
kd_sell_condition = (k < k.shift(1)) & (d < d.shift(1))

# 停損條件：MACD DIF 向下
macd_dif_sell_condition = dif < dif.shift(1)

# 合併所有賣出條件
sell_signal = dmi_sell_condition & kd_sell_condition & macd_dif_sell_condition

# 最終的持倉訊號
position = buy_signal.hold_until(sell_signal)

# 執行回測
from finlab.backtest import sim

report = sim(position, resample=None, upload=False)
report.display()
