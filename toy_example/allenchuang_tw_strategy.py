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
foreign_net_buy_ratio = foreign_net_buy / shares_outstanding
foreign_self_net_buy_ratio = foreign_self_net_buy / shares_outstanding
investment_trust_net_buy_ratio = investment_trust_net_buy / shares_outstanding
dealer_self_net_buy_ratio = dealer_self_net_buy / shares_outstanding
dealer_hedge_net_buy_ratio = dealer_hedge_net_buy / shares_outstanding

# 計算3天和5天的累積買超比例
total_net_buy_3d_sum = (foreign_net_buy_ratio.rolling(3).sum() +
                        foreign_self_net_buy_ratio.rolling(3).sum() +
                        investment_trust_net_buy_ratio.rolling(3).sum() +
                        dealer_self_net_buy_ratio.rolling(3).sum() +
                        dealer_hedge_net_buy_ratio.rolling(3).sum())

total_net_buy_5d_sum = (foreign_net_buy_ratio.rolling(5).sum() +
                        foreign_self_net_buy_ratio.rolling(5).sum() +
                        investment_trust_net_buy_ratio.rolling(5).sum() +
                        dealer_self_net_buy_ratio.rolling(5).sum() +
                        dealer_hedge_net_buy_ratio.rolling(5).sum())


top_n = 20

# 取前3天和5天累積買超比例最大的股票
chip_3d_top_n_buy_signal = total_net_buy_3d_sum.rank(axis=1, ascending=False) <= top_n
chip_5d_top_n_buy_signal = total_net_buy_5d_sum.rank(axis=1, ascending=False) <= top_n

# 籌碼面
chip_condition = chip_3d_top_n_buy_signal | chip_5d_top_n_buy_signal


# 獲取收盤價數據
adj_close = data.get('etl:adj_close')

# 計算均線
ma5 = adj_close.rolling(5).mean()
ma10 = adj_close.rolling(10).mean()
ma20 = adj_close.rolling(20).mean()
ma60 = adj_close.rolling(60).mean()

# 均線上升
ma_up_condition = (ma5 > ma5.shift(1)) & (ma10 > ma10.shift(1)) & (ma20 > ma20.shift(1)) & (ma60 > ma60.shift(1))

# 價格在均線之上
price_above_ma_condition = (adj_close > ma5) & (adj_close > ma10) & (adj_close > ma20) & (adj_close > ma60)

# 計算乖離率
bias_10 = (adj_close - ma10) / ma10
bias_20 = (adj_close - ma20) / ma20

# 乖離率小於0.14
bias_condition = (bias_10.abs() < 0.14) & (bias_20.abs() < 0.14)

# 獲取成交量數據
volume = data.get('price:成交股數')

# 成交量大於昨日的2.5倍
volume_condition = volume > (volume.shift(1) * 2.5)

# 計算DMI指標
plus_di = data.indicator('PLUS_DI', timeperiod=14, adjust_price=True)
minus_di = data.indicator('MINUS_DI', timeperiod=14, adjust_price=True)

# DMI條件
dmi_condition = (plus_di > 40) & (minus_di < 18)

# 技術面
technical_condition = ma_up_condition & price_above_ma_condition & bias_condition & volume_condition & dmi_condition

# 最終的買入訊號
buy_signal = chip_condition & technical_condition

# 計算 MACD 指標
macd, signal, hist = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)
dif = macd
macd_9 = signal

# 停損條件：DIF 和 MACD 向下
macd_down_condition = (dif < dif.shift(1)) & (macd_9 < macd_9.shift(1))

# 停損條件：+DI 小於 -DI
dmi_down_condition = plus_di < minus_di

# 最終的賣出訊號
sell_signal  = macd_down_condition & dmi_down_condition

position = buy_signal.hold_until(sell_signal)

# 執行回測
from finlab.backtest import sim

report = sim(position, resample=None, upload=False)
report.display()
