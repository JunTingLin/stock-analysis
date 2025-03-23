from finlab import data
from finlab.markets.tw import TWMarket
from finlab.backtest import sim

class AdjustTWMarketInfo(TWMarket):
    def get_trading_price(self, name, adj=True):
        return self.get_price(name, adj=adj).shift(1)


class AllenChuangBasicTWStrategy:
    def get_trading_price(self, name, adj=True):
        return self.get_price(name, adj=adj).shift(1)
    
    def run_strategy(self):

        with data.universe(market='TSE_OTC'):
            close = data.get("price:收盤價")
            adj_close = data.get('etl:adj_close')
            adj_open = data.get('etl:adj_open')

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


        # 設定進場乖離率
        bias_buy_condition = (
                            (bias_5 <= 0.12) & (bias_5 >= 0.02) &
                            (bias_10 <= 0.15) & (bias_10 >= 0.05) &
                            (bias_20 <= 0.20) & (bias_20 >= 0.05) &
                            (bias_60 <= 0.20) & (bias_60 >= 0.05) & 
                            (bias_120 <= 0.25) & (bias_120 >= 0.10) &
                            (bias_240 <= 0.25) & (bias_240 >= 0.10)
                            )

        # 今收盤 > 今開盤，且今收盤 > 昨收盤
        positive_close_condition = (adj_close > adj_open) & (adj_close > adj_close.shift(1))

        price_above_15_condition = close > 15

        with data.universe(market='TSE_OTC'):
            # 獲取成交量數據
            volume = data.get('price:成交股數')

        # 成交量大於昨日的2倍
        volume_doubled_condition = volume > (volume.shift(1) * 2)

        # 今日成交張數 > 500 張
        volume_above_500_condition = volume > 500 * 1000

        with data.universe(market='TSE_OTC'):
            # 計算DMI指標
            plus_di = data.indicator('PLUS_DI', timeperiod=14, adjust_price=True)
            minus_di = data.indicator('MINUS_DI', timeperiod=14, adjust_price=True)

        # DMI條件
        dmi_buy_condition = (plus_di > 24) & (minus_di < 21)

        with data.universe(market='TSE_OTC'):
            # 計算 KD 指標
            k, d = data.indicator('STOCH', fastk_period=9, slowk_period=3, slowd_period=3, adjust_price=True)

        # KD 指標條件：%K 和 %D 都向上
        kd_buy_condition = (k > k.shift(1)) & (d > d.shift(1))

        with data.universe(market='TSE_OTC'):
            # 計算 MACD 指標
            dif, macd , _  = data.indicator('MACD', fastperiod=12, slowperiod=26, signalperiod=9, adjust_price=True)

        # MACD DIF 向上
        macd_dif_buy_condition = dif > dif.shift(1)

        # 創新高
        high_120 = adj_close.rolling(window=120).max()
        new_high_120_condition = adj_close >= high_120
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
            price_above_15_condition &

            dmi_buy_condition & 
            kd_buy_condition & 
            macd_dif_buy_condition &
            new_high_condition
        )

        with data.universe(market='TSE_OTC'):
            # 取得月營收及去年同月增減(%)資料
            monthly_revenue = data.get('monthly_revenue:當月營收')
            monthly_revenue_yoy = data.get('monthly_revenue:去年同月增減(%)')
            operating_margin = data.get('fundamental_features:營業利益率')
            gross_margin = data.get('fundamental_features:營業毛利率')

        # 判斷連續兩個月的 YOY 增長是否均達到 20%
        revenue_yoy_increase = monthly_revenue_yoy >= 20
        consecutive_revenue_yoy = revenue_yoy_increase & revenue_yoy_increase.shift(1)

        # 判斷近3個月平均營收是否大於過去12個月平均營收
        revenue_3m_avg = monthly_revenue.rolling(window=3).mean()
        revenue_12m_avg = monthly_revenue.rolling(window=12).mean()
        revenue_growth = revenue_3m_avg > revenue_12m_avg

        # 營業利益率比上期增加 10% ~ 25%
        # operating_margin_growth = (operating_margin - operating_margin.shift(1)) / operating_margin.shift(1)
        # operating_margin_increase = (operating_margin_growth > 0.10) \
        #                             & (operating_margin_growth <= 0.25)

        operating_margin_increase = (operating_margin > (operating_margin.shift(1) * 1.25)) \
                                    #  & (operating_margin <= (operating_margin.shift(1) * 1.25))

        # 營業利益率大於 2%
        # operating_margin_increase = operating_margin > 2

        # 毛利率的成長率
        gross_margin_condition = gross_margin > gross_margin.shift(1) * 1.05

        # 基本面
        fundamental_buy_condition =  operating_margin_increase


        # 最終的買入訊號
        buy_signal =  technical_buy_condition & fundamental_buy_condition

        # 設定起始買入日期
        start_buy_date = '2017-12-31'
        buy_signal = buy_signal.loc[start_buy_date:]

        # ### 賣出條件
        ## 法一: 短線出場
        sell_condition = (ma3 < ma3.shift(1)) & (dif < dif.shift(1))

        ## 法二: 中線出場
        # sell_condition = (ma5 < ma5.shift(1)) & (dif < dif.shift(1)) & (macd < macd.shift(1)) & (adj_close < ma20)

        position = buy_signal.hold_until(sell_condition)

        self.report = sim(position, resample=None, upload=False, market=AdjustTWMarketInfo())
        
        return self.report

    def get_report(self):
        return self.report if self.report else "report物件為空，請先運行策略"
