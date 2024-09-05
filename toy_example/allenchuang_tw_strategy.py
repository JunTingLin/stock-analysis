from finlab import data

# 獲取三大法人的買賣超數據
foreign_net_buy = data.get('institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)')
foreign_self_net_buy = data.get('institutional_investors_trading_summary:外資自營商買賣超股數')
investment_trust_net_buy = data.get('institutional_investors_trading_summary:投信買賣超股數')
dealer_self_net_buy = data.get('institutional_investors_trading_summary:自營商買賣超股數(自行買賣)')
dealer_hedge_net_buy = data.get('institutional_investors_trading_summary:自營商買賣超股數(避險)')

# 直接使用發行股數作為總股數
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


# 設定買入條件，例如前10名
top_n = 10

# 取前3天和5天累積買超比例最大的股票
buy_signal_3d = total_net_buy_3d_sum.rank(axis=1, ascending=False) <= top_n
buy_signal_5d = total_net_buy_5d_sum.rank(axis=1, ascending=False) <= top_n

# 最終的買入訊號，選擇3天或5天買超排行較高的股票
buy_signal = buy_signal_3d | buy_signal_5d

# 執行回測
from finlab.backtest import sim

report = sim(buy_signal, resample='q')
report.display()
