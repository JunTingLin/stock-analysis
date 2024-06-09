from finlab import data, backtest

class PeterWuTWStrategyNStock10:
    def __init__(self):
        self.data = data
        self.market_value = None
        self.close = None
        self.eps = None
        self.revenue_growth_yoy = None
        self.report = None
        self.position = None
        self.company_basic_info = None

    def load_data(self):
        with self.data.universe(market='TSE_OTC'):
            self.market_value = self.data.get("etl:market_value")
            self.close = self.data.get("price:收盤價")
            self.eps = self.data.get('financial_statement:每股盈餘')
            self.revenue_growth_yoy = self.data.get('monthly_revenue:去年同月增減(%)')
            self.company_basic_info = self.data.get('company_basic_info')

    def run_strategy(self):
        if self.close is None:
            self.load_data()

        # 計算季線（60日移動平均）並判斷季線是否上升
        ma60 = self.close.average(60)
        ma60_rising = ma60.rise(1)

        # 股價是否大於季線
        above_ma60 = self.close > ma60
        # 股價突破三個月高點
        high_3m = self.close.rolling(60).max()
        price_break_high_3m = self.close >= high_3m

        # 過去四個季度的盈餘總和大於2元，且連續兩年都滿足這個條件
        cumulative_eps_last_year = self.eps.rolling(4).sum() > 2
        cumulative_eps_year_before_last = self.eps.shift(4).rolling(4).sum() > 2
        eps_condition = cumulative_eps_last_year & cumulative_eps_year_before_last

        # 設定營業額成長的條件
        revenue_growth_condition = self.revenue_growth_yoy > 30

        # 買入條件
        buy_condition = (
            above_ma60 &
            ma60_rising &
            price_break_high_3m &
            eps_condition &
            revenue_growth_condition
        )

        below_ma60 = self.close < ma60
        not_recover_in_5_days = below_ma60.sustain(5)
        ma60_falling = ma60 < ma60.shift(1)
        price_change_percent = self.close.pct_change()
        hit_drop_limit = price_change_percent <= -0.10

        # 賣出條件
        sell_condition = (
            not_recover_in_5_days |
            ma60_falling |
            hit_drop_limit
        )

        self.position = buy_condition.hold_until(sell_condition)

        # 設定起始日期
        start_date = '2015-12-31'
        self.position = self.position.loc[start_date:]

        # 現在將市值數據整合進來，每個重平衡周期選出市值前10大的股票
        self.position = self.market_value[self.position].is_largest(10)

        # 使用 sim 函數進行模擬
        self.report = backtest.sim(self.position, resample='M', name="吳Peter策略選股_10檔", upload="False")
        return self.report

    def get_report(self):
        return self.report if self.report else "report物件為空，請先運行策略"

    def get_close_prices(self):
        return self.close if self.close is not None else "收盤價數據未加載，請先運行策略"

    def get_company_basic_info(self):
        return self.company_basic_info if self.company_basic_info is not None else "公司基本信息未加載，請先運行策略"


strategy = PeterWuTWStrategyNStock10()
strategy.run_strategy()
print(strategy.get_report())
