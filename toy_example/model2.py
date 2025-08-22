from finlab import data
from finlab.markets.tw import TWMarket
import pandas as pd
import numpy as np
from taiwan_kd import taiwan_kd_fast

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

def build_chip_buy_condition(top_n):
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
    foreign_top_1d_ratio = foreign_net_buy_ratio.rank(axis=1, ascending=False) <= top_n
    foreign_top_2d_ratio = foreign_net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= top_n
    foreign_top_3d_ratio = foreign_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= top_n
    foreign_buy_condition = foreign_top_1d_ratio | foreign_top_2d_ratio | foreign_top_3d_ratio

    # 投信：取當天、前2天、前3天累積買超比例前幾
    investment_trust_top_1d_ratio = investment_trust_net_buy_ratio.rank(axis=1, ascending=False) <= top_n
    investment_trust_top_2d_ratio = investment_trust_net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= top_n
    investment_trust_top_3d_ratio = investment_trust_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= top_n
    investment_trust_buy_condition = investment_trust_top_1d_ratio | investment_trust_top_2d_ratio | investment_trust_top_3d_ratio

    # 自營商：取當天、前2天、前3天累積買超比例前幾
    dealer_self_top_1d_ratio = dealer_self_net_buy_ratio.rank(axis=1, ascending=False) <= top_n
    dealer_self_top_2d_ratio = dealer_self_net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= top_n
    dealer_self_top_3d_ratio = dealer_self_net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= top_n
    dealer_self_buy_condition = dealer_self_top_1d_ratio | dealer_self_top_2d_ratio | dealer_self_top_3d_ratio

    # institutional_investors_top_buy_condition = foreign_buy_condition | investment_trust_buy_condition | dealer_self_buy_condition

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
    main_force_top_1d_buy = net_buy_ratio.rank(axis=1, ascending=False) <= top_n
    main_force_top_2d_buy = net_buy_ratio_2d_sum.rank(axis=1, ascending=False) <= top_n
    main_force_top_3d_buy = net_buy_ratio_3d_sum.rank(axis=1, ascending=False) <= top_n
    main_force_condition_1d = net_buy_ratio > 0.0008
    main_force_condition_2d = net_buy_ratio_2d_sum > 0.0015
    main_force_condition_3d = net_buy_ratio_3d_sum > 0.0025

    main_force_buy_condition = ( main_force_top_1d_buy & main_force_condition_1d ) | ( main_force_top_2d_buy & main_force_condition_2d ) | ( main_force_top_3d_buy & main_force_condition_3d )

    chip_buy_condition = foreign_buy_condition | dealer_self_buy_condition | main_force_buy_condition

    return {
        'chip_buy_condition': chip_buy_condition,
        'foreign_buy_condition': foreign_buy_condition,
        'investment_trust_buy_condition': investment_trust_buy_condition,
        'dealer_self_buy_condition': dealer_self_buy_condition,
        'main_force_buy_condition': main_force_buy_condition
    }

with data.universe(market='TSE_OTC'):
    close = data.get("price:收盤價")
    high = data.get("price:最高價")
    low = data.get("price:最低價")
    adj_close = data.get('etl:adj_close')
    adj_open = data.get('etl:adj_open')
    volume = data.get('price:成交股數')

def build_technical_buy_condition():

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

    bias_5_condition = (bias_5 <= 0.12) & (bias_5 >= 0.02)
    bias_10_condition = (bias_10 <= 0.15) & (bias_10 >= 0.05)
    bias_20_condition = (bias_20 <= 0.20) & (bias_20 >= 0.05)
    bias_60_condition = (bias_60 <= 0.20) & (bias_60 >= 0.05)
    bias_120_condition = (bias_120 <= 0.25) & (bias_120 >= 0.10)
    bias_240_condition = (bias_240 <= 0.25) & (bias_240 >= 0.10)


    # 設定進場乖離率
    bias_buy_condition = (
                        bias_5_condition &
                        bias_10_condition &
                        bias_20_condition &
                        bias_60_condition & 
                        bias_120_condition &
                        bias_240_condition
                        )

    # 今收盤 > 今開盤，且今收盤 > 昨收盤
    positive_close_condition = (adj_close > adj_open) & (adj_close > adj_close.shift(1))

    price_above_12_condition = close > 12

    # 成交量大於昨日的2倍
    volume_doubled_condition = volume > (volume.shift(1) * 2)

    # 今日成交張數 > 500 張
    volume_above_500_condition = volume > 500 * 1000

    # 成交金額大於 3000 萬
    amount_condition = (close * volume) > 30000000

    with data.universe(market='TSE_OTC'):
        # 計算DMI指標
        plus_di = data.indicator('PLUS_DI', timeperiod=14, adjust_price=True)
        minus_di = data.indicator('MINUS_DI', timeperiod=14, adjust_price=True)

    # DMI條件
    dmi_buy_condition = (plus_di > 24) & (minus_di < 21)

    # 計算 KD 指標
    with data.universe(market='TSE_OTC'):
        k, d = data.indicator('STOCH',
                                fastk_period=9, 
                                slowk_period=3, 
                                slowk_matype=0,
                                slowd_period=3,
                                slowd_matype=0,
                                adjust_price=True
                                )
    # k, d = taiwan_kd_fast(
    #     high_df=high,
    #     low_df=low,
    #     close_df=close,
    #     fastk_period=9,
    #     alpha=1/3
    # )
    

    # KD 指標條件：%K 和 %D 都向上
    k_up_condition = k > k.shift(1)
    d_up_condition = d > d.shift(1)
    kd_buy_condition = k_up_condition & d_up_condition

    with data.universe(market='TSE_OTC'):
        # 計算 MACD 指標
        dif, macd , _  = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)

    # MACD DIF 向上
    macd_dif_buy_condition = dif > dif.shift(1)

    # 創新高
    high_120 = adj_close.rolling(window=120).max()
    new_high_120_condition = adj_close >= high_120 * 0.95
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
        price_above_12_condition &
        amount_condition &

        dmi_buy_condition & 
        kd_buy_condition & 
        macd_dif_buy_condition &
        new_high_condition
    )
    
    return {
        'technical_buy_condition': technical_buy_condition,
        'ma_up_buy_condition': ma_up_buy_condition,
        'price_above_ma_buy_condition': price_above_ma_buy_condition,
        'bias_buy_condition': bias_buy_condition,
        'volume_doubled_condition': volume_doubled_condition,
        'volume_above_500_condition': volume_above_500_condition,
        'price_above_12_condition': price_above_12_condition,
        'amount_condition': amount_condition,
        'dmi_buy_condition': dmi_buy_condition,
        'kd_buy_condition': kd_buy_condition,
        'macd_dif_buy_condition': macd_dif_buy_condition,
        'new_high_condition': new_high_condition,

        'bias_values': {
            'bias_5': bias_5,
            'bias_10': bias_10,
            'bias_20': bias_20,
            'bias_60': bias_60,
            'bias_120': bias_120,
            'bias_240': bias_240
        },
        'bias_conditions': {
            'bias_5_condition': bias_5_condition,
            'bias_10_condition': bias_10_condition,
            'bias_20_condition': bias_20_condition,
            'bias_60_condition': bias_60_condition,
            'bias_120_condition': bias_120_condition,
            'bias_240_condition': bias_240_condition
        },

        'kd_values': {
            'k_value': k,
            'd_value': d
        },
        'kd_conditions': {
            'k_up_condition': k_up_condition,
            'd_up_condition': d_up_condition,
            'kd_buy_condition': kd_buy_condition
        }
    }

with data.universe(market='TSE_OTC'):
    operating_margin = data.get('fundamental_features:營業利益率')

def build_fundamental_buy_condition(op_growth_threshold):

    # operating_margin_deadline = operating_margin.deadline()

    operating_margin_increase = (operating_margin > (operating_margin.shift(1) * op_growth_threshold))

    fundamental_buy_condition = (
        operating_margin_increase
        # rd_pm_top100
        # eq_top100
    )

    return {
        'fundamental_buy_condition': fundamental_buy_condition,
        'operating_margin_increase': operating_margin_increase,
    }


# 最終的買入訊號
chip_conditions = build_chip_buy_condition(top_n=5)
tech_conditions = build_technical_buy_condition()
fund_conditions = build_fundamental_buy_condition(1.20)

buy_signal = (
    chip_conditions['chip_buy_condition'] &
    tech_conditions['technical_buy_condition'] &
    fund_conditions['fundamental_buy_condition']
)


# 設定起始買入日期
start_buy_date = '2017-12-31'
buy_signal = buy_signal.loc[start_buy_date:]

# volume_ma = volume.average(10)
# buy_signal = volume_ma * buy_signal
# buy_signal = buy_signal.is_largest(5)

def build_sell_condition():
    ma3 = adj_close.rolling(3).mean()
    dif, macd , _  = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)

    # 法一: 短線出場
    sell_condition = (ma3 < ma3.shift(1)) & (dif < dif.shift(1))

    # 法二: 中線出場
    # sell_condition = (ma5 < ma5.shift(1)) & (dif < dif.shift(1)) & (macd < macd.shift(1)) & (adj_close < ma20)


    return sell_condition

sell_condition = build_sell_condition()
position = buy_signal.hold_until(sell_condition)


# 執行回測
from finlab.backtest import sim

# report = sim(position, resample=None, upload=False, trade_at_price='close')
report = sim(position, resample=None, upload=False, market=AdjustTWMarketInfo())
# report = sim(position, resample=None, upload=False, trade_at_price='open', position_limit=0.25, fee_ratio=0.02, tax_ratio=0)


# ----
def diagnose_strategy(target_stocks, analysis_days, top_n, start_date, fundamental_quarter):

    print("🔍 診斷策略條件")
    print("="*80)
    
    # 調用策略函數獲取所有條件
    print("📊 計算籌碼面條件...")
    chip_conditions = build_chip_buy_condition(top_n)
    
    print("📊 計算技術面條件...")
    tech_conditions = build_technical_buy_condition()
    
    print("📊 計算基本面條件...")
    fund_conditions = build_fundamental_buy_condition(1.20)
    
    # 獲取分析日期 - 從指定日期開始往後取analysis_days天
    buy_signal_dates = chip_conditions['chip_buy_condition'].index
    start_date = pd.to_datetime(start_date)
    
    # 找到起始日期在index中的位置
    if start_date in buy_signal_dates:
        start_idx = buy_signal_dates.get_loc(start_date)
        end_idx = min(start_idx + analysis_days, len(buy_signal_dates))
        latest_dates = buy_signal_dates[start_idx:end_idx]
    else:
        # 如果指定的日期不在index中，找到最接近且大於等於該日期的日期
        valid_dates = buy_signal_dates[buy_signal_dates >= start_date]
        if len(valid_dates) == 0:
            print(f"❌ 指定的起始日期 {start_date.strftime('%Y-%m-%d')} 超出數據範圍")
            print(f"   數據範圍: {buy_signal_dates[0].strftime('%Y-%m-%d')} 到 {buy_signal_dates[-1].strftime('%Y-%m-%d')}")
            return
        
        closest_date = valid_dates[0]
        start_idx = buy_signal_dates.get_loc(closest_date)
        end_idx = min(start_idx + analysis_days, len(buy_signal_dates))
        latest_dates = buy_signal_dates[start_idx:end_idx]
        
        if closest_date != start_date:
            print(f"⚠️  指定日期 {start_date.strftime('%Y-%m-%d')} 不在交易日中，使用最接近的交易日 {closest_date.strftime('%Y-%m-%d')}")
    
    print(f"📅 分析日期: {latest_dates[0].strftime('%Y-%m-%d')} 到 {latest_dates[-1].strftime('%Y-%m-%d')} (共{len(latest_dates)}天)")
    
    # 檢查股票是否存在
    available_stocks = []
    for stock in target_stocks:
        if stock in chip_conditions['chip_buy_condition'].columns:
            available_stocks.append(stock)
        else:
            print(f"⚠️  股票 {stock} 不在數據中")
    
    if not available_stocks:
        print("❌ 沒有可分析的股票")
        return
    
    print(f"📈 分析股票: {available_stocks}")
    
    # 顯示籌碼面條件
    print(f"\n{'='*20} 籌碼面條件 {'='*20}")
    for name, condition in chip_conditions.items():
        print(f"\n{name}:")
        try:
            result = condition[available_stocks].loc[latest_dates]
            print(result)
        except:
            print("⚠️  數據不可用")
    
    # 顯示技術面條件（排除 bias 和 kd 詳細分析）
    print(f"\n{'='*20} 技術面條件 {'='*20}")
    excluded_keys = ['bias_values', 'bias_conditions', 'kd_values', 'kd_conditions']
    for name, condition in tech_conditions.items():
        if name not in excluded_keys:
            print(f"\n{name}:")
            try:
                result = condition[available_stocks].loc[latest_dates]
                print(result)
            except:
                print("⚠️  數據不可用")
    
    # 🎯 新增：詳細的 Bias 分析區塊
    print(f"\n{'='*20} 🔍 BIAS 乖離率詳細分析 {'='*20}")
    
    # 顯示 bias 實際數值
    print(f"\n📊 Bias 數值 (百分比格式):")
    bias_values = tech_conditions['bias_values']
    for bias_name, bias_data in bias_values.items():
        print(f"\n{bias_name}:")
        try:
            result = bias_data[available_stocks].loc[latest_dates]
            # 轉換成百分比格式顯示
            result_percent = result * 100
            print(result_percent.round(2))
        except:
            print("⚠️  數據不可用")
    
    # 顯示各個 bias 條件的 True/False 狀況
    print(f"\n✅ Bias 條件判斷 (True/False):")
    bias_conditions = tech_conditions['bias_conditions']
    bias_ranges = {
        'bias_5_condition': '(2% ≤ bias_5 ≤ 12%)',
        'bias_10_condition': '(5% ≤ bias_10 ≤ 15%)',
        'bias_20_condition': '(5% ≤ bias_20 ≤ 20%)',
        'bias_60_condition': '(5% ≤ bias_60 ≤ 20%)',
        'bias_120_condition': '(10% ≤ bias_120 ≤ 25%)',
        'bias_240_condition': '(10% ≤ bias_240 ≤ 25%)'
    }
    
    for condition_name, condition_data in bias_conditions.items():
        print(f"\n{condition_name} {bias_ranges[condition_name]}:")
        try:
            result = condition_data[available_stocks].loc[latest_dates]
            print(result)
        except:
            print("⚠️  數據不可用")
    
    # 顯示整體 bias_buy_condition
    print(f"\n🎯 整體 bias_buy_condition (所有條件都滿足):")
    try:
        result = tech_conditions['bias_buy_condition'][available_stocks].loc[latest_dates]
        print(result)
    except:
        print("⚠️  數據不可用")

        # 🆕 詳細的 KD 指標分析區塊
    print(f"\n{'='*20} 📈 KD 指標詳細分析 {'='*20}")
    
    # 顯示 KD 實際數值
    print(f"\n📊 KD 指標數值:")
    kd_values = tech_conditions['kd_values']
    for kd_name, kd_data in kd_values.items():
        print(f"\n{kd_name}:")
        try:
            result = kd_data[available_stocks].loc[latest_dates]
            print(result.round(2))
        except:
            print("⚠️  數據不可用")
    
    # 顯示各個 KD 條件的 True/False 狀況
    print(f"\n✅ KD 條件判斷 (True/False):")
    kd_conditions = tech_conditions['kd_conditions']
    kd_descriptions = {
        'k_up_condition': '(%K 向上: K > K前一日)',
        'd_up_condition': '(%D 向上: D > D前一日)', 
        'kd_buy_condition': '(KD買入條件: K向上 且 D向上)'
    }
    
    for condition_name, condition_data in kd_conditions.items():
        print(f"\n{condition_name} {kd_descriptions[condition_name]}:")
        try:
            result = condition_data[available_stocks].loc[latest_dates]
            print(result)
        except:
            print("⚠️  數據不可用")
    
    # 顯示基本面條件 (處理季度數據)
    print(f"\n{'='*20} 基本面條件 {'='*20}")
    
    # 處理用戶指定的季度
    print(f"📊 使用指定季度: {fundamental_quarter}")
    try:
        # 檢查指定的季度是否存在於數據中
        fundamental_data = fund_conditions['fundamental_buy_condition']
        available_quarters = fundamental_data.index.tolist()
        
        if fundamental_quarter in available_quarters:
            target_quarter = fundamental_quarter
            print(f"✅ 找到指定季度: {target_quarter}")
        else:
            print(f"❌ 指定季度 {fundamental_quarter} 不存在於數據中")
            print(f"📋 可用的季度: {available_quarters}")
            print("❌ 請重新指定一個有效的季度")
            return  # 直接退出，不繼續分析
    except Exception as e:
        print(f"❌ 處理指定季度時發生錯誤: {e}")
        print("❌ 請檢查季度格式是否正確 (例如: '2025-Q1')")
        return  # 直接退出，不繼續分析
    
    # 顯示基本面各個條件
    for name, condition in fund_conditions.items():
        print(f"\n{name} (季度: {target_quarter}):")
        try:
            result = condition[available_stocks].loc[[target_quarter]]
            print(result)
        except Exception as e:
            print(f"⚠️  數據不可用: {e}")
    
    # 最終組合條件
    print(f"\n{'='*20} 最終組合條件 {'='*20}")
    
    final_chip = chip_conditions['chip_buy_condition']
    final_tech = tech_conditions['technical_buy_condition'] 
    final_fund = fund_conditions['fundamental_buy_condition']
    
    print(f"\n🎯 籌碼面總條件:")
    try:
        result = final_chip[available_stocks].loc[latest_dates]
        print(result)
    except:
        print("⚠️  數據不可用")
    
    print(f"\n🎯 技術面總條件:")
    try:
        result = final_tech[available_stocks].loc[latest_dates]
        print(result)
    except:
        print("⚠️  數據不可用")
    
    print(f"\n🎯 基本面總條件 (季度: {target_quarter}):")
    try:
        quarter_result = final_fund[available_stocks].loc[[target_quarter]]
        print(quarter_result)
        print(f"(此 {target_quarter} 季度結果會應用到分析期間的所有日期)")
    except:
        print("⚠️  數據不可用")

print("🚀 開始診斷...")
# diagnose_strategy(['8033'], analysis_days=10, top_n=5, start_date='2025-07-17', fundamental_quarter='2025-Q1')
# diagnose_strategy(['8358'], analysis_days=10, top_n=5, start_date='2025-07-04', fundamental_quarter='2025-Q1')
diagnose_strategy(['2402'], analysis_days=10, top_n=5, start_date='2025-08-07', fundamental_quarter='2025-Q1')