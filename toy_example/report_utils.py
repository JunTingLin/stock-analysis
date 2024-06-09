from report_utils import SignalAnalyzer, ReportAnalyzer, ReportSaver

position = None
report = None

# 處理信號
analyzer = SignalAnalyzer(position)
clean_signals = analyzer.remove_never_bought_stocks()
print(clean_signals)

# 分析報告
analyzer = ReportAnalyzer(report)
analysis_result = analyzer.analyze_trades_for_date('2024-03-01')
print(analysis_result)

# 保存報告和交易記錄
saver = ReportSaver(report)
saver.save_report_html()
saver.save_trades_excel()
