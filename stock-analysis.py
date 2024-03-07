import pandas as pd
from finlab import data
from finlab import backtest
from get_data import get_data_from_finlab

close = get_data_from_finlab("price:收盤價", use_cache=True, market='TSE_OTC')
market_value = get_data_from_finlab("etl:market_value", use_cache=True, market='TSE_OTC')
market_value = market_value[:'2020-12-31 00:00:00']
eps = get_data_from_finlab('financial_statement:每股盈餘', use_cache=True, market='TSE_OTC')

# with data.universe(market='TSE_OTC'):
#     close = data.get('price:收盤價')
#     market_value = data.get('etl:market_value')

# 計算季線（60日移動平均）並判斷季線是否上升
ma60 = close.average(60)
ma60_rising = ma60 > ma60.shift(1)
# # 股價是否大於季線
above_ma60 = close > ma60
# 股價突破三個月高點
high_3m = close.rolling(60).max()
price_break_high_3m = close >= high_3m
# 總市值在150億台幣以上
market_value_condition = market_value > 15000000000  # 150億台幣
# 過去四個季度的盈餘總和大於2元，且連續兩年都滿足這個條件
cumulative_eps_last_year = eps.rolling(4).sum() > 2
cumulative_eps_year_before_last = eps.shift(4).rolling(4).sum() > 2
eps_condition = cumulative_eps_last_year & cumulative_eps_year_before_last


# 買入條件
buy_condition = (
    above_ma60 &
    ma60_rising &
    price_break_high_3m &
    market_value_condition &
    eps_condition
)

below_ma60 = close < ma60
not_recover_in_5_days = below_ma60.sustain(5)
ma60_falling = ma60 < ma60.shift(1)
# 計算每天股票價格相比前一天收盤價的變動百分比
price_change_percent = close.pct_change()
# 設定停板條件，即價格跌幅小於或等於-10%
hit_drop_limit = price_change_percent <= -0.10


# 賣出條件
sell_condition = ( not_recover_in_5_days | ma60_falling | hit_drop_limit )

position = buy_condition.hold_until(sell_condition)

# 使用 sim 函數進行模擬
report = backtest.sim(position, resample=None, name="吳Peter策略選股")


if __name__ == "__main__":
    # 保存報告和交易記錄
    from report_saver import save_report_html, save_trades_excel

    save_report_html(report)
    save_trades_excel(report)

