import pandas as pd
from finlab import backtest
from get_data import get_data_from_finlab

close = get_data_from_finlab("price:收盤價", use_cache=True)
market_value = get_data_from_finlab("etl:market_value", use_cache=True)

# 計算季線（60日移動平均）並判斷季線是否上升
ma60 = close.average(60)
ma60_rising = ma60 > ma60.shift(1)
# # 股價是否大於季線
above_ma60 = close > ma60
# 股價突破三個月高點
high_3m = close.rolling(60).max()
price_break_high_3m = close >= high_3m
# 總市值在150億台幣以上
# market_value_condition = market_value > 15000000000  # 150億台幣

# 綜合買入條件
buy_condition = (
    above_ma60 &
    ma60_rising &
    price_break_high_3m
    # market_value_condition
)

# 使用 sim 函數進行模擬
report = backtest.sim(buy_condition, resample='D', name="吳Peter策略選股")


# 顯示回測報告
# report.display()

html_content = report.display().data
with open("report.html", "w") as f:
    f.write(html_content)

# 然後手動在您的網頁瀏覽器中打開 "report.html"
