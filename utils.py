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