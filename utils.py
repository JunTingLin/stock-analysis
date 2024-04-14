import numpy as np

def calculate_slope(y):
    """
    使用最小平法計算給定時間序列的線性迴歸斜率。
    
    參數：
    - y: 一維隊列或列表，表示時間序列的值。
    
    返回:
    - m: 線性迴歸的斜率。
    """
    # 移除 NaN 值
    y = y[~np.isnan(y)]
    x = np.arange(len(y))

    if len(y) < 2:  # 如果資料點少於2，無法計算斜率
        return np.nan

    A = np.vstack([x, np.ones(len(x))]).T
    m, b = np.linalg.lstsq(A, y, rcond=None)[0]
    return m

def calculate_rolling_slope(series, window=60):
    """
    計算每天前N天的收盤價的線性迴歸斜率。
    """
    return series.rolling(window=window).apply(calculate_slope, raw=False)

        
def get_daily_changes(signal_df, date):
    if date not in signal_df.index:
        raise ValueError("The specified date is not available in the position DataFrame.")
        
    # 將訊號向前移動一天，以反映實際交易發生的日期
    positions = signal_df.shift(1).astype(bool)
    
    #確保資料為布林類型
    current_positions = positions.loc[date].astype(bool)
    previous_positions = positions.shift(1).loc[date].astype(bool)
    
    # 新買入的股票：當天持有且前一天未持有
    buys = current_positions & ~previous_positions
    
    # 賣出的股票：前一天持有且當天未持有
    sells = ~current_positions & previous_positions
    
    # 繼續持有的股票：當天持有且前一天也持有
    holds = current_positions & previous_positions
    
    return {
        'buys': list(buys[buys].index),
        'sells': list(sells[sells].index),
        'holds': list(holds[holds].index)
    }