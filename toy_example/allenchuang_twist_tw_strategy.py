from finlab import data, backtest

with data.universe(market='TSE_OTC'):
    adj_close = data.get('etl:adj_close')

# 計算5日、10日、20日均線
ma5 = adj_close.rolling(5).mean()
ma10 = adj_close.rolling(10).mean()
ma20 = adj_close.rolling(20).mean()

with data.universe(market='TSE_OTC'):
    # 計算 DI+ 和 DI- 指標
    plus_di = data.indicator('PLUS_DI', timeperiod=14, adjust_price=True)
    minus_di = data.indicator('MINUS_DI', timeperiod=14, adjust_price=True)

# 根據均線條件計算分數
ma_score = (
    ((adj_close > ma5) & (adj_close > ma10) & (adj_close > ma20)).astype(int) * 2 +  # 收盤價高於5、10、20日均線：+2分
    ((adj_close > ma5) & (adj_close > ma10) & (adj_close < ma20)).astype(int) * 1 +  # 收盤價高於5、10日均線但低於20日均線：+1分
    ((adj_close < ma5) & (adj_close > ma10) & (adj_close > ma20)).astype(int) * 1 +  # 收盤價低於5日但高於10、20日均線：+1分
    ((adj_close < ma5) & (adj_close < ma10) & (adj_close > ma20)).astype(int) * -1 + # 收盤價低於5、10日均線但高於20日均線：-1分
    ((adj_close < ma5) & (adj_close < ma10) & (adj_close < ma20)).astype(int) * -2   # 收盤價低於5、10、20日均線：-2分
)

# 根據 +DI 和 -DI 計算分數
di_score = (
    (plus_di > 35).astype(int) * 2 +  # +DI 大於35：+2分
    ((plus_di >= 21) & (plus_di <= 35)).astype(int) * 1 +  # +DI 在21到35之間：+1分
    ((plus_di >= 18) & (plus_di <= 21)).astype(int) * -1 +  # +DI 在18到21之間：-1分
    (plus_di < 18).astype(int) * -2 +  # +DI 小於18：-2分
    (minus_di > 35).astype(int) * -2 +  # -DI 大於35：-2分
    ((minus_di >= 21) & (minus_di <= 35)).astype(int) * -1 +  # -DI 在21到35之間：-1分
    ((minus_di >= 18) & (minus_di <= 21)).astype(int) * 1 +  # -DI 在18到21之間：+1分
    (minus_di < 18).astype(int) * 2  # -DI 小於18：+2分
)

with data.universe(market='TSE_OTC'):
    # 計算 MACD、DIF 和 KD 指標
    dif, macd, _ = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)
    k, d = data.indicator('STOCH', fastk_period=9, slowk_period=3, slowd_period=3, adjust_price=True)

# 根據均線和 DMI 計算的總分
total_score = ma_score + di_score

# 首先保存第14點和第15點所需的條件
adjust_down = (total_score < 5)
adjust_up = (total_score > -5)

# 第14條：當總分小於 +5 時，根據 DIF、MACD 和 KD 分別調整分數
# DIF 向下扣 1 分
dif_down = (dif < dif.shift(1)) & adjust_down
total_score_adjusted = total_score - dif_down.astype(int)

# MACD 向下再扣 1 分
macd_down = (macd < macd.shift(1)) & adjust_down
total_score_adjusted = total_score_adjusted - macd_down.astype(int)

# K 和 D 同時向下再扣 1 分
kd_down = (k < k.shift(1)) & (d < d.shift(1)) & adjust_down
total_score_adjusted = total_score_adjusted - kd_down.astype(int)

# 第15條：當總分大於 -5 時，根據 DIF、MACD 和 KD 分別調整分數
# DIF 向上加 1 分
dif_up = (dif > dif.shift(1)) & adjust_up
total_score_adjusted = total_score_adjusted + dif_up.astype(int)

# MACD 向上再加 1 分
macd_up = (macd > macd.shift(1)) & adjust_up
total_score_adjusted = total_score_adjusted + macd_up.astype(int)

# K 和 D 同時向上再加 1 分
kd_up = (k > k.shift(1)) & (d > d.shift(1)) & adjust_up
total_score_adjusted = total_score_adjusted + kd_up.astype(int)

# 根據條件1和2判斷低檔轉折和高檔轉折
# 低檔轉折條件：總分由負轉平及轉正，且 KD、DIF 同時轉上
low_turn = (total_score_adjusted.shift(1) < 0) & (total_score_adjusted >= 0) & (dif > dif.shift(1)) & (k > k.shift(1))

# 高檔轉折條件：總分由正轉平及轉負，且 KD、DIF 同時轉下
high_turn = (total_score_adjusted.shift(1) > 0) & (total_score_adjusted <= 0) & (dif < dif.shift(1)) & (k < k.shift(1))

# 設定持倉：在低檔轉折時買入，在高檔轉折時賣出
position = low_turn.hold_until(high_turn)


# 進行回測，使用每週調整持倉
report = backtest.sim(position, resample=None)