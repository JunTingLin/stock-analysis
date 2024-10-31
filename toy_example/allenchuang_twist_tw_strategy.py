from finlab import data, backtest
import talib
from talib import abstract
import pandas as pd

# 取得台股加權指數（TAIEX）的資料
market_data_open = data.get('taiex_total_index:開盤指數')
market_data_high = data.get('taiex_total_index:最高指數')
market_data_low = data.get('taiex_total_index:最低指數')
market_data_close = data.get('taiex_total_index:收盤指數')

# 使用 TAIEX 的開高低收指數並篩選 2024 年之後的資料
taiex_data = pd.DataFrame({
    'open': market_data_open['TAIEX'].loc['2024-01-01':],
    'high': market_data_high['TAIEX'].loc['2024-01-01':],
    'low': market_data_low['TAIEX'].loc['2024-01-01':],
    'close': market_data_close['TAIEX'].loc['2024-01-01':]
})

# 計算5日、10日、20日均線
ma5 = taiex_data['close'].rolling(5).mean()
ma10 = taiex_data['close'].rolling(10).mean()
ma20 = taiex_data['close'].rolling(20).mean()

# 計算 DI+ 和 DI- 指標，加入 timeperiod 參數
plus_di = abstract.Function('PLUS_DI')(taiex_data, timeperiod=14)
minus_di = abstract.Function('MINUS_DI')(taiex_data, timeperiod=14)

# 根據均線條件計算分數
ma_score = (
    ((taiex_data['close'] > ma5) & (taiex_data['close'] > ma10) & (taiex_data['close'] > ma20)).astype(int) * 2 +  # 收盤價高於5、10、20日均線：+2分
    ((taiex_data['close'] > ma5) & (taiex_data['close'] > ma10) & (taiex_data['close'] < ma20)).astype(int) * 1 +  # 收盤價高於5、10日均線但低於20日均線：+1分
    ((taiex_data['close'] < ma5) & (taiex_data['close'] > ma10) & (taiex_data['close'] > ma20)).astype(int) * 1 +  # 收盤價低於5日但高於10、20日均線：+1分
    ((taiex_data['close'] < ma5) & (taiex_data['close'] < ma10) & (taiex_data['close'] > ma20)).astype(int) * -1 + # 收盤價低於5、10日均線但高於20日均線：-1分
    ((taiex_data['close'] < ma5) & (taiex_data['close'] < ma10) & (taiex_data['close'] < ma20)).astype(int) * -2   # 收盤價低於5、10、20日均線：-2分
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

# 計算 MACD 和 KD 指標
dif, macd, _ = talib.MACD(taiex_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
k, d = talib.STOCH(taiex_data['high'], taiex_data['low'], taiex_data['close'], fastk_period=9, slowk_period=3, slowd_period=3)

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