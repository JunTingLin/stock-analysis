from finlab import data
from finlab.backtest import sim

close = data.get("price:收盤價")
vol = data.get("price:成交股數")
vol_ma = vol.average(10)
rev = data.get('monthly_revenue:當月營收')
rev_year_growth = data.get('monthly_revenue:去年同月增減(%)')
rev_month_growth = 	data.get('monthly_revenue:上月比較增減(%)')

# 股價創年新高
cond1 = (close == close.rolling(250).max())

# 排除月營收連3月衰退10%以上
cond2 = ~(rev_year_growth < -10).sustain(3) 

# 排除月營收成長趨勢過老(12個月內有至少8個月單月營收年增率大於60%)
cond3 = ~(rev_year_growth > 60).sustain(12,8)

# 確認營收底部，近月營收脫離近年谷底(連續3月的"單月營收近12月最小值/近月營收" < 0.8)
cond4 = ((rev.rolling(12).min())/(rev) < 0.8).sustain(3)

# 單月營收月增率連續3月大於-40%
cond5 = (rev_month_growth > -40).sustain(3)

# 流動性條件
cond6 = vol_ma > 200*1000

buy = cond1 & cond2  & cond3 & cond4 & cond5 & cond6

# 買比較冷門的股票
buy = vol_ma*buy
buy = buy[buy>0]
buy = buy.is_smallest(5)

report = sim(buy , resample="M", upload=False, position_limit=1/3, fee_ratio=1.425/1000/3, stop_loss=0.08,  trade_at_price='open',name='藏獒', live_performance_start='2022-05-01')


from report_analyzer import ReportAnalyzer
# 分析報告
analyzer = ReportAnalyzer(report)
analysis_result = analyzer.analyze_trades_for_date('2024-03-01')
print(analysis_result)

from report_saver import ReportSaver
# 保存報告和交易記錄
saver = ReportSaver(report)
saver.save_report_html()
saver.save_trades_excel()

from report_analyzer import ReportAnalyzer
# 分析報告
analyzer = ReportAnalyzer(report)
analysis_result = analyzer.analyze_trades_for_date('2024-03-01')
print(analysis_result)