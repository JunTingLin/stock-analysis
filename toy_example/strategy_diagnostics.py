import pandas as pd

def diagnose_strategy(target_stocks, analysis_days, chip_conditions, tech_conditions, fund_conditions, start_date, fundamental_quarter=None):
    """
    通用策略診斷函數
    
    參數:
    - target_stocks: 要分析的股票代碼列表
    - analysis_days: 要分析的天數
    - chip_conditions: 籌碼面條件字典
    - tech_conditions: 技術面條件字典 
    - fund_conditions: 基本面條件字典
    - start_date: 起始分析日期
    - fundamental_quarter: 基本面季度 (可選)
    """
    
    print("🔍 診斷策略條件")
    print("="*80)
    
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
    
    # 詳細的 Bias 分析區塊
    if 'bias_values' in tech_conditions and 'bias_conditions' in tech_conditions:
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
            print(f"\n{condition_name} {bias_ranges.get(condition_name, '')}:")
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

    # 詳細的 KD 指標分析區塊
    if 'kd_values' in tech_conditions and 'kd_conditions' in tech_conditions:
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
            print(f"\n{condition_name} {kd_descriptions.get(condition_name, '')}:")
            try:
                result = condition_data[available_stocks].loc[latest_dates]
                print(result)
            except:
                print("⚠️  數據不可用")
    
    # 顯示基本面條件 (處理季度數據)
    print(f"\n{'='*20} 基本面條件 {'='*20}")
    
    # 處理用戶指定的季度
    if fundamental_quarter:
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
    else:
        # 如果沒有指定季度，顯示最新可用的季度
        for name, condition in fund_conditions.items():
            print(f"\n{name}:")
            try:
                result = condition[available_stocks].tail(1)
                print(result)
            except:
                print("⚠️  數據不可用")
    
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
    
    if fundamental_quarter:
        print(f"\n🎯 基本面總條件 (季度: {target_quarter}):")
        try:
            quarter_result = final_fund[available_stocks].loc[[target_quarter]]
            print(quarter_result)
            print(f"(此 {target_quarter} 季度結果會應用到分析期間的所有日期)")
        except:
            print("⚠️  數據不可用")
    else:
        print(f"\n🎯 基本面總條件:")
        try:
            result = final_fund[available_stocks].tail(1)
            print(result)
        except:
            print("⚠️  數據不可用")
