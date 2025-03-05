from finlab import data
from finlab.backtest import sim

class PrisonRabbitStrategy:
    def __init__(self):
        self.report = None

    def run_strategy(self):
        處置股資訊 = data.get('disposal_information').sort_index()
        close = data.get("price:收盤價")
        position = close < 0

        # 將不是分盤交易的處置雜訊過濾
        處置股資訊 = 處置股資訊[~處置股資訊["分時交易"].isna()].dropna(how='all')

        # date 為盤後處置股公告日，作為訊號產生日。
        處置股資訊 = 處置股資訊.reset_index()[["stock_id", "date", "處置結束時間"]]
        處置股資訊.columns = ["stock_id", "處置開始時間", "處置結束時間"]

        for i in range(0, 處置股資訊.shape[0]):
            stock_id = 處置股資訊.iloc[i, 0]
            # 排除股票代號等於4碼的標地才納入(以普通股為主，排除特殊金融商品)
            if len(stock_id) == 4:
                start_day = 處置股資訊.iloc[i, 1]
                end_day = 處置股資訊.iloc[i, 2]
                # 處置時間期間持有
                position.loc[start_day:end_day, stock_id] = True

        self.report = sim(position, trade_at_price="open", fee_ratio=1.425/1000/3, position_limit=0.2, name='監獄兔')
        return self.report

    def get_report(self):
        return self.report if self.report else "report物件為空，請先運行策略"

# Example usage:
strategy = PrisonRabbitStrategy()
report = strategy.run_strategy()
print(report)