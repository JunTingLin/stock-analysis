from finlab import data
#  finlab 版本 < 1.2.20
# from finlab.market_info import TWMarketInfo
#  finlab 版本 >= 1.2.20
from finlab.markets.tw import TWMarket
import pandas as pd
import numpy as np

class AdjustTWMarketInfo(TWMarket):
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

# 計算外資、投信、自營商的2天、3天累積買超比例
foreign_net_buy_ratio_2d_sum = foreign_net_buy_ratio.rolling(2).sum()
foreign_net_buy_ratio_3d_sum = foreign_net_buy_ratio.rolling(3).sum()

investment_trust_net_buy_ratio_2d_sum = investment_trust_net_buy_ratio.rolling(2).sum()
investment_trust_net_buy_ratio_3d_sum = investment_trust_net_buy_ratio.rolling(3).sum()

dealer_self_net_buy_ratio_2d_sum = dealer_self_net_buy_ratio.rolling(2).sum()
dealer_self_net_buy_ratio_3d_sum = dealer_self_net_buy_ratio.rolling(3).sum()


# 外資：取當天、前2天、前3天累積買超比例前幾
foreign_top_1d_ratio = foreign_net_buy_ratio.rank(axis=1, ascending=False) <= 3
foreign_top_2d_ratio = foreign_net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= 3
foreign_top_3d_ratio = foreign_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 5
foreign_buy_condition = foreign_top_1d_ratio | foreign_top_2d_ratio | foreign_top_3d_ratio

# 投信：取當天、前2天、前3天累積買超比例前幾
investment_trust_top_1d_ratio = investment_trust_net_buy_ratio.rank(axis=1, ascending=False) <= 3
investment_trust_top_2d_ratio = investment_trust_net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= 3
investment_trust_top_3d_ratio = investment_trust_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 5
investment_trust_buy_condition = investment_trust_top_1d_ratio | investment_trust_top_2d_ratio | investment_trust_top_3d_ratio

# 自營商：取當天、前2天、前3天累積買超比例前幾
dealer_self_top_1d_ratio = dealer_self_net_buy_ratio.rank(axis=1, ascending=False) <= 3
dealer_self_top_2d_ratio = dealer_self_net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= 3
dealer_self_top_3d_ratio = dealer_self_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 5
dealer_self_buy_condition = dealer_self_top_1d_ratio | dealer_self_top_2d_ratio | dealer_self_top_3d_ratio

institutional_investors_top_buy_condition = foreign_buy_condition | investment_trust_buy_condition | dealer_self_buy_condition

# with data.universe(market='TSE_OTC'):
#     # 獲取每檔股票的收盤價數據
#     close_price = data.get('price:收盤價')

# # 計算三大法人的買超金額
# foreign_total_net_buy_amount = foreign_net_buy_shares  * close_price  # 外資
# investment_trust_net_buy_amount = investment_trust_net_buy_shares * close_price  # 投信
# dealer_total_net_buy_amount = dealer_self_net_buy_shares * close_price  # 自營商

# # 計算三大法人的總買超金額
# total_net_buy_amount = foreign_total_net_buy_amount + investment_trust_net_buy_amount + dealer_total_net_buy_amount

# # 計算2天、3天的累積買超金額之和
# total_net_buy_amount_2d_sum = total_net_buy_amount.rolling(2).sum()
# total_net_buy_amount_3d_sum = total_net_buy_amount.rolling(3).sum()

# # 取當天、前2天、前3天、前5天買超金額前幾
# total_market_top_1d = total_net_buy_amount.rank(axis=1, ascending=False) <= 3
# total_market_top_2d = total_net_buy_amount_2d_sum.rank(axis=1, ascending=False) <= 3
# total_market_top_3d = total_net_buy_amount_3d_sum.rank(axis=1, ascending=False) <= 3

# total_market_top_intersection = total_market_top_1d & total_market_top_2d & total_market_top_3d

with data.universe(market='TSE_OTC'):
    # 獲取主力籌碼數據 (買超和賣超)
    top15_buy_shares = data.get('etl:broker_transactions:top15_buy')
    top15_sell_shares = data.get('etl:broker_transactions:top15_sell')

# 計算買賣超差額股數
net_buy_shares = (top15_buy_shares - top15_sell_shares) * 1000

# 買賣超差額股數佔發行股數的比例
net_buy_ratio = net_buy_shares / shares_outstanding

# 計算2天、3天買賣超差額股數佔發行股數的比
net_buy_ratio_2d_sum = net_buy_ratio.rolling(2).sum()
net_buy_ratio_3d_sum = net_buy_ratio.rolling(3).sum()

# 主力籌碼條件
main_force_top_1d_buy = net_buy_ratio.rank(axis=1, ascending=False) <= 3
main_force_top_2d_buy = net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= 3
main_force_top_3d_buy = net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= 3
main_force_condition_1d = net_buy_ratio > 0.008
main_force_condition_2d = net_buy_ratio_2d_sum > 0.015
main_force_condition_3d = net_buy_ratio_3d_sum > 0.025

main_force_buy_condition = ( main_force_top_1d_buy & main_force_condition_1d ) | ( main_force_top_2d_buy & main_force_condition_2d ) | ( main_force_top_3d_buy & main_force_condition_3d )

chip_buy_condition = institutional_investors_top_buy_condition | main_force_buy_condition

with data.universe(market='TSE_OTC'):
    adj_close = data.get('etl:adj_close')
    adj_open = data.get('etl:adj_open')

# 計算均線
ma3 = adj_close.rolling(3).mean()
ma5 = adj_close.rolling(5).mean()
ma10 = adj_close.rolling(10).mean()
ma20 = adj_close.rolling(20).mean()
ma60 = adj_close.rolling(60).mean()
ma120 = adj_close.rolling(120).mean()
ma240 = adj_close.rolling(240).mean()

# 均線上升
ma_up_buy_condition = (ma5 > ma5.shift(1)) & (ma10 > ma10.shift(1)) & (ma20 > ma20.shift(1)) & (ma60 > ma60.shift(1))

# 5 日線大於 60/240 日線
ma5_above_others_condition = (ma5 > ma60) & (ma5 > ma240)

# 價格在均線之上
price_above_ma_buy_condition = (adj_close > ma5) & (adj_close > ma10) & (adj_close > ma20) & (adj_close > ma60)

# 計算乖離率
bias_5 = (adj_close - ma5) / ma5
bias_10 = (adj_close - ma10) / ma10
bias_20 = (adj_close - ma20) / ma20
bias_60 = (adj_close - ma60) / ma60
bias_120 = (adj_close - ma120) / ma120
bias_240 = (adj_close - ma240) / ma240


# 設定進場條件為乖離率在正向且小於 0.14
# bias_buy_condition = ((bias_10 < 0.14) & (bias_10 > 0) &
#                       (bias_20 < 0.14) & (bias_20 > 0) &
#                       (bias_60 <= 0.20) & (bias_60 >= 0.05) & 
#                       (bias_240 <= 0.25) & (bias_240 >= 0.10))

bias_buy_condition = (
                    (bias_5 <= 0.12) & (bias_5 >= 0.02) &
                    (bias_10 <= 0.15) & (bias_10 >= 0.05) &
                    (bias_20 <= 0.20) & (bias_20 >= 0.05) &
                    (bias_60 <= 0.20) & (bias_60 >= 0.05) & 
                    (bias_120 <= 0.25) & (bias_120 >= 0.10) &
                    (bias_240 <= 0.25) & (bias_240 >= 0.10)
                    )

with data.universe(market='TSE_OTC'):
    # 獲取成交量數據
    volume = data.get('price:成交股數')

# 成交量大於昨日的2倍
volume_doubled_condition = volume > (volume.shift(1) * 2)

# 今收盤 > 今開盤，且今收盤 > 昨收盤
positive_close_condition = (adj_close > adj_open) & (adj_close > adj_close.shift(1))

# 今日成交張數 > 500 張
volume_above_500_condition = volume > 500 * 1000

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

# 創新高
high_120 = adj_close.rolling(window=120).max()
new_high_120_condition = adj_close >= high_120
new_high_condition = new_high_120_condition

# 技術面
technical_buy_condition = (
    ma_up_buy_condition & 
    # ma5_above_others_condition &
    price_above_ma_buy_condition & 
    bias_buy_condition & 
    volume_doubled_condition & 
    # positive_close_condition &
    volume_above_500_condition &

    dmi_buy_condition & 
    kd_buy_condition & 
    macd_dif_buy_condition &
    new_high_condition
)

# 最終的買入訊號
buy_signal = chip_buy_condition & technical_buy_condition

# 設定起始買入日期
start_buy_date = '2017-12-31'
buy_signal = buy_signal.loc[start_buy_date:]

# ### 賣出條件
## 法一: 短線出場
sell_condition = (ma3 < ma3.shift(1)) & (dif < dif.shift(1))

## 法二: 中線出場
# sell_condition = (ma5 < ma5.shift(1)) & (dif < dif.shift(1)) & (macd < macd.shift(1)) & (adj_close < ma20)

position = buy_signal.hold_until(sell_condition)


# 執行回測
from finlab.backtest import sim

# report = sim(position, resample=None, upload=False, trade_at_price='close')
report = sim(position, resample=None, upload=False, market=AdjustTWMarketInfo())


# ===============================================================================

import matplotlib.pyplot as plt

def plot_bias_vs_return(bias, trades, bias_name):
    bias_values = []
    trade_returns = []

    for date, stock_id, trade_return in zip(trades['entry_sig_date'], trades['stock_id'], trades['return']):
        stock_id = stock_id.split()[0]  # 提取股票代號
        if date in bias.index and stock_id in bias.columns:
            # 獲取該筆交易的 bias 和 return，並轉換為百分比
            bias_values.append(bias.loc[date, stock_id])
            trade_returns.append(trade_return * 100)  # 回報轉換為百分比

    # 將數據轉為 pandas Series
    bias_values = pd.Series(bias_values, name=bias_name)
    trade_returns = pd.Series(trade_returns, name="Return (%)")

    # 確認數據大小是否一致
    print(f"Number of {bias_name} values: {len(bias_values)}")
    print(f"Number of Return values: {len(trade_returns)}")

    # 散點圖：展示 bias 與 Return 的關係
    plt.figure(figsize=(10, 6))
    plt.scatter(bias_values, trade_returns, alpha=0.7, color="blue", label=f"{bias_name} vs Return")
    plt.axhline(0, color='red', linestyle='--', linewidth=0.8)  # 基準線
    plt.title(f"Scatter Plot of {bias_name} vs Return")
    plt.xlabel(bias_name)
    plt.ylabel("Return (%)")
    plt.grid(True)
    plt.legend()
    plt.show()

    # 直方圖
    bins = np.arange(0, bias_values.max() + 0.05, 0.05)  # 每 5% 一個區間
    bias_return_df = pd.DataFrame({bias_name: bias_values, "Return (%)": trade_returns})
    bias_return_df[f"{bias_name}_Bins"] = pd.cut(bias_return_df[bias_name], bins=bins)
    average_return_per_bin = bias_return_df.groupby(f"{bias_name}_Bins")["Return (%)"].mean()

    # 繪製直方圖
    average_return_per_bin.plot(kind="bar", figsize=(12, 6), color="green", alpha=0.7)
    plt.title(f"Average Return per {bias_name} Interval")
    plt.xlabel(f"{bias_name} Interval")
    plt.ylabel("Average Return (%)")
    plt.grid(True)
    plt.show()

    # 輸出統計數據
    print(f"Average Return per {bias_name} Interval:")
    print(average_return_per_bin)

# 提取交易報告中的交易信息
trades = report.get_trades()

# 確定離群值閾值，例如回報超過 500%
outlier_threshold = 5  # 500%
outliers = trades[trades["return"] > outlier_threshold]
print(f"Outliers:\n{outliers}")

# 移除離群值
# trades = trades[trades["return"] <= outlier_threshold]

# Plot for Bias_5
plot_bias_vs_return(bias_5, trades, "Bias_5")

# Plot for Bias_10
plot_bias_vs_return(bias_10, trades, "Bias_10")

# Plot for Bias_20
plot_bias_vs_return(bias_20, trades, "Bias_20")

# Plot for Bias_120
plot_bias_vs_return(bias_120, trades, "Bias_120")