import pandas as pd
from finlab import data
from finlab.backtest import sim
from utils.config_loader import ConfigLoader
from dao.recommendation_dao import RecommendationDAO

class RogerTWStrategyBase:
    def __init__(self, task_name, config_path="config.yaml"):
        self.task_name = task_name  # 'weekly' or 'monthly'
        self.report = None
        self.config_loader = ConfigLoader(config_path)

    def _create_position_df(self, universe):
        """
        讀取推薦 DAO 並轉換為 Finlab 可用的 Position DataFrame
        支援 stocks 為物件列表，從 stock.id 取代號
        """  
        dao = RecommendationDAO(frequency=self.task_name)
        recommendation_records = dao.load()

        records = []
        for record in recommendation_records:
            date = record.date
            stocks = record.stocks
            if not date or not stocks:
                continue

            dt = pd.to_datetime(date)
            for stock in stocks:
                stock_id = getattr(stock, 'id', None)
                if not stock_id:
                    continue
                records.append({
                    'date': dt,
                    'stock_id': str(stock_id),
                    'signal': 1
                })

        if not records:
            return None

        df = pd.DataFrame(records)
        df = df.drop_duplicates(subset=['date', 'stock_id'])
        
        position = df.pivot(index='date', columns='stock_id', values='signal')
        position = position.fillna(0)
        
        # 轉為每日資料並 Forward Fill
        position = position.resample('D').ffill()

        # 對齊日期範圍
        latest_market_date = universe.index.max()
        if latest_market_date > position.index.max():
            extended_index = pd.date_range(start=position.index.min(), end=latest_market_date, freq='D')
            position = position.reindex(extended_index, method='ffill')
        
        # 對齊全市場股票代號
        position = position.reindex(columns=universe.columns, fill_value=0)
        
        return position.astype(bool)

    def run_strategy(self):
        universe = data.get('price:收盤價')
        position = self._create_position_df(universe)
        self.report = sim(position=position, resample='W-MON', fee_ratio=1.425/1000, tax_ratio=3/1000, upload=False)
        
        return self.report

    def get_report(self):
        return self.report if self.report else "report物件為空，請先運行策略"