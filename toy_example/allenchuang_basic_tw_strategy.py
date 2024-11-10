from finlab import data
from finlab.market_info import TWMarketInfo
import pandas as pd
import numpy as np

class AdjustTWMarketInfo(TWMarketInfo):
    def get_trading_price(self, name, adj=True):
        return self.get_price(name, adj=adj).shift(1)

with data.universe(market='TSE_OTC'):
    # 獲取三大法人的買賣超股數數據
    foreign_net_buy_shares = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')
    investment_trust_net_buy_shares = data.get('institutional_investors_trading_summary:投信買賣超股數')
    dealer_self_net_buy_shares = data.get('institutional_investors_trading_summary:自營商買賣超股數(自行買賣)')
    # 發行股數作為總股數
    shares_outstanding = data.get('internal_equity_changes:發行股數')

# 計算外資、投信、自營商的買賣超佔發行量比例 (股數)
foreign_net_buy_ratio = foreign_net_buy_shares / shares_outstanding
investment_trust_net_buy_ratio = investment_trust_net_buy_shares / shares_outstanding
dealer_self_net_buy_ratio = dealer_self_net_buy_shares / shares_outstanding

# 計算外資、投信、自營商的3天和5天累積買超比例
foreign_net_buy_ratio_3d_sum = foreign_net_buy_ratio.rolling(3).sum()
foreign_net_buy_ratio_5d_sum = foreign_net_buy_ratio.rolling(5).sum()

investment_trust_net_buy_ratio_3d_sum = investment_trust_net_buy_ratio.rolling(3).sum()
investment_trust_net_buy_ratio_5d_sum = investment_trust_net_buy_ratio.rolling(5).sum()

dealer_self_net_buy_ratio_3d_sum = dealer_self_net_buy_ratio.rolling(3).sum()
dealer_self_net_buy_ratio_5d_sum = dealer_self_net_buy_ratio.rolling(5).sum()


# 外資：取當天、前3天、前5天累積買超比例前幾
foreign_top_1d_ratio = foreign_net_buy_ratio.rank(axis=1, ascending=False) <= 3
foreign_top_3d_ratio = foreign_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 5
foreign_top_5d_ratio = foreign_net_buy_ratio_5d_sum.rank(axis=1, ascending=False) <= 5
foreign_buy_condition = foreign_top_1d_ratio  | foreign_top_3d_ratio | foreign_top_5d_ratio

# 投信：取當天、前3天、前5天累積買超比例前幾
investment_trust_top_1d_ratio = investment_trust_net_buy_ratio.rank(axis=1, ascending=False) <= 3
investment_trust_top_3d_ratio = investment_trust_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 5
investment_trust_top_5d_ratio = investment_trust_net_buy_ratio_5d_sum.rank(axis=1, ascending=False) <= 5
investment_trust_buy_condition = investment_trust_top_1d_ratio | investment_trust_top_3d_ratio | investment_trust_top_5d_ratio

# 自營商：取當天、前3天、前5天累積買超比例前幾
dealer_self_top_1d_ratio = dealer_self_net_buy_ratio.rank(axis=1, ascending=False) <= 3
dealer_self_top_3d_ratio = dealer_self_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 5
dealer_self_top_5d_ratio = dealer_self_net_buy_ratio_5d_sum.rank(axis=1, ascending=False) <= 5
dealer_self_buy_condition = dealer_self_top_1d_ratio | dealer_self_top_3d_ratio | dealer_self_top_5d_ratio

institutional_investors_top_buy_condition = foreign_buy_condition | investment_trust_buy_condition | dealer_self_buy_condition

with data.universe(market='TSE_OTC'):
    # 獲取每檔股票的收盤價數據
    close_price = data.get('price:收盤價')

# 計算三大法人的買超金額
foreign_total_net_buy_amount = foreign_net_buy_shares  * close_price  # 外資
investment_trust_net_buy_amount = investment_trust_net_buy_shares * close_price  # 投信
dealer_total_net_buy_amount = dealer_self_net_buy_shares * close_price  # 自營商

# 計算三大法人的總買超金額
total_net_buy_amount = foreign_total_net_buy_amount + investment_trust_net_buy_amount + dealer_total_net_buy_amount

# 計算3天和5天的累積買超金額之和
total_net_buy_amount_3d_sum = total_net_buy_amount.rolling(3).sum()
total_net_buy_amount_5d_sum = total_net_buy_amount.rolling(5).sum()


# 取當天、前3天、前5天買超金額前幾
total_market_top_1d = total_net_buy_amount.rank(axis=1, ascending=False) <= 3
total_market_top_3d = total_net_buy_amount_3d_sum.rank(axis=1, ascending=False) <= 3
total_market_top_5d = total_net_buy_amount_5d_sum.rank(axis=1, ascending=False) <= 3

total_market_top_intersection = total_market_top_1d & total_market_top_3d & total_market_top_5d

with data.universe(market='TSE_OTC'):
    # 獲取主力籌碼數據 (買超和賣超)
    top15_buy_shares = data.get('etl:broker_transactions:top15_buy')
    top15_sell_shares = data.get('etl:broker_transactions:top15_sell')

# 計算買賣超差額股數
net_buy_shares = (top15_buy_shares - top15_sell_shares) * 1000

# 買賣超差額股數佔發行股數的比例
net_buy_ratio = net_buy_shares / shares_outstanding
# 計算當天買超股數佔發行股數的比例
buy_ratio = top15_buy_shares / shares_outstanding

# 計算3天和5天買賣超股數佔發行股數的比
net_buy_ratio_3d_sum = net_buy_ratio.rolling(3).sum()
net_buy_ratio_5d_sum = net_buy_ratio.rolling(5).sum()

# 主力籌碼條件
main_force_top_1d_buy = buy_ratio.rank(axis=1, ascending=False) <= 3
main_force_condition_3d = net_buy_ratio_3d_sum > 0.025
main_force_condition_5d = net_buy_ratio_5d_sum > 0.025

main_force_buy_condition = main_force_top_1d_buy | main_force_condition_3d | main_force_condition_5d

chip_buy_condition = institutional_investors_top_buy_condition  | total_market_top_intersection | main_force_buy_condition

with data.universe(market='TSE_OTC'):
    # 獲取收盤價數據
    adj_close = data.get('etl:adj_close')

# 計算均線
ma3 = adj_close.rolling(3).mean()
ma5 = adj_close.rolling(5).mean()
ma10 = adj_close.rolling(10).mean()
ma20 = adj_close.rolling(20).mean()
ma60 = adj_close.rolling(60).mean()
ma240 = adj_close.rolling(240).mean()

# 均線上升
ma_up_buy_condition = (ma5 > ma5.shift(1)) & (ma10 > ma10.shift(1)) & (ma20 > ma20.shift(1)) & (ma60 > ma60.shift(1))

# 5 日線大於 60/240 日線
ma5_above_others_condition = (ma5 > ma60) & (ma5 > ma240)

# 價格在均線之上
price_above_ma_buy_condition = (adj_close > ma5) & (adj_close > ma10) & (adj_close > ma20) & (adj_close > ma60)

# 計算乖離率
bias_10 = (adj_close - ma10) / ma10
bias_20 = (adj_close - ma20) / ma20
bias_60 = (adj_close - ma60) / ma60
bias_240 = (adj_close - ma240) / ma240


# 設定進場條件為乖離率在正向且小於 0.14
bias_buy_condition = ((bias_10 < 0.14) & (bias_10 > 0) &
                      (bias_20 < 0.14) & (bias_20 > 0) &
                      (bias_60 <= 0.21) & (bias_60 >= 0.01) & 
                      (bias_240 <= 0.25) & (bias_240 >= 0.01))

with data.universe(market='TSE_OTC'):
    # 獲取成交量數據
    volume = data.get('price:成交股數')

# 成交量大於昨日的2.5倍
volume_buy_condition = volume > (volume.shift(1) * 2)

with data.universe(market='TSE_OTC'):
    # 計算DMI指標
    plus_di = data.indicator('PLUS_DI', timeperiod=14, adjust_price=True)
    minus_di = data.indicator('MINUS_DI', timeperiod=14, adjust_price=True)

# DMI條件
dmi_buy_condition = (plus_di > 24) & (minus_di < 21)

with data.universe(market='TSE_OTC'):
    # 計算 KD 指標
    k, d = data.indicator('STOCH', fastk_period=9, slowk_period=3, slowd_period=3, adjust_price=True)

# KD 指標條件：%K 和 %D 都向上
kd_buy_condition = (k > k.shift(1)) & (d > d.shift(1))

with data.universe(market='TSE_OTC'):
    # 計算 MACD 指標
    dif, macd , _  = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)

# MACD DIF 向上
macd_dif_buy_condition = dif > dif.shift(1)

# 技術面
technical_buy_condition = (
    ma_up_buy_condition & 
    ma5_above_others_condition &
    price_above_ma_buy_condition & 
    bias_buy_condition & 
    volume_buy_condition & 
    dmi_buy_condition & 
    kd_buy_condition & 
    macd_dif_buy_condition
)

# 最終的買入訊號
buy_signal = chip_buy_condition & technical_buy_condition

# 設定起始買入日期
# start_buy_date = '2017-12-31'
# buy_signal = buy_signal.loc[start_buy_date:]

# ### 賣出條件
# 法一
sell_condition_1 = (ma5 < ma5.shift(1)) & (dif < dif.shift(1)) & (macd < macd.shift(1)) & (adj_close < ma20)  # 日線向下，DIF、MACD 雙線向下，收盤價小於 20 日均線
sell_condition_2 = (ma3 < ma3.shift(1)) & (dif < dif.shift(1))  # 3 日均線向下，DIF 向下

# 獲取聯集的日期索引 (index) 和交集的股票代碼 (columns)
combined_index = buy_signal.index.union(sell_condition_1.index).union(sell_condition_2.index)
combined_columns = buy_signal.columns.intersection(sell_condition_1.columns).intersection(sell_condition_2.columns)

position = pd.DataFrame(0.0, index=combined_index, columns=combined_columns)

import time
start_time = time.time()

# 初始化持倉，直接對 `DataFrame` 操作
for stock in position.columns:
    for day in range(1, len(position)):
        prev_index = position.index[day-1]
        current_index = position.index[day]

        try:
            # 如果前一天持倉為 1.0 且 sell_condition_1 發生，將持倉設為 0.5
            if position.at[prev_index, stock] == 1.0 and sell_condition_1.at[current_index, stock]:
                position.at[current_index, stock] = 0.5
            # 如果前一天持倉為 0.5 且 sell_condition_2 發生，將持倉設為 0.0
            elif position.at[prev_index, stock] == 0.5 and sell_condition_2.at[current_index, stock]:
                position.at[current_index, stock] = 0.0
            # 如果當天買入訊號為 True 且前一天持倉為 0，將持倉設為 1.0
            elif position.at[prev_index, stock] == 0.0 and buy_signal.at[current_index, stock]:
                position.at[current_index, stock] = 1.0
            # 否則保持前一天的持倉狀態
            else:
                position.at[current_index, stock] = position.at[prev_index, stock]
        
        except KeyError:
            # 遇到 KeyError 時，保持前一天的持倉狀態
            position.at[current_index, stock] = position.at[prev_index, stock]
            
end_time = time.time()
execution_time = end_time - start_time
print("程式執行時間：", execution_time, "秒")

# 法二
sell_condition = (ma5 < ma5.shift(1)) & (dif < dif.shift(1)) & (macd < macd.shift(1)) & (adj_close < ma20)  # 日線向下，DIF、MACD 雙線向下，收盤價小於 20 日均線
position = buy_signal.hold_until(sell_condition)


# 執行回測
from finlab.backtest import sim

# report = sim(position, resample=None, upload=False, trade_at_price='close')
report = sim(position, resample=None, upload=False, market=AdjustTWMarketInfo())
