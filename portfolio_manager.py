from data_persistence_manager import DataPersistenceManager
from utils import is_trading_day
from finlab.online.order_executor import Position, OrderExecutor
import logging
from decimal import Decimal
import os


class PortfolioManager:
    def __init__(self, acc, fund, strategy_class_name, datetime, extra_bid_pct):
        self.acc = acc
        self.fund = fund
        self.strategy = self.load_strategy(strategy_class_name)
        self.datetime = datetime
        self.extra_bid_pct = extra_bid_pct
        self.data_dict = {}
        self.data_manager = DataPersistenceManager()

    def load_strategy(self, strategy_class_name):
        if strategy_class_name == 'TibetanMastiffTWStrategy':
            from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
        elif strategy_class_name == 'PeterWuStrategy':
            from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
        else:
            raise ValueError(f"Unknown strategy class: {strategy_class_name}")
        return strategy_class()
    
    def execute_order(self):
        report = self.strategy.run_strategy()
        position_acc = self.acc.get_position()
        position_today = Position.from_report(report, self.fund, odd_lot=True)
        position_today = self.rebalance_portfolio(position_today, position_acc)

        if position_today is not None:
            order_executor = OrderExecutor(position_today, account=self.acc)
            # order_executor.create_orders(extra_bid_pct=self.extra_bid_pct)

        self.update_data_dict(position_today, position_acc)

        return self.data_dict

        
    def rebalance_portfolio(self, position_today, position_acc):
        # 獲取今日和現有持倉的股票ID集合
        new_ids = set(p['stock_id'] for p in position_today.position)
        current_ids = set(p['stock_id'] for p in position_acc.position)

        # 判斷需要新增或移除的股票ID
        add_ids = new_ids - current_ids
        remove_ids = current_ids - new_ids

        try:
            if add_ids:
                # 如果有新增的股票，回傳今日持倉以進行相應操作
                logging.info(f"新增股票ID: {add_ids}")
                return position_today

            if remove_ids:
                # 如果有移除的股票，更新今日持倉並設定該股票的數量為0
                logging.info(f"移除股票ID: {remove_ids}")
                updated_positions = []
                for position in position_acc.position:
                    if position['stock_id'] in remove_ids:
                        position['quantity'] = Decimal('0')
                    updated_positions.append(position)
                position_today.position = updated_positions
                return position_today

            # 如果無需新增或移除，回傳None表示持倉無需變化
            logging.info("持倉無需變化")
            return None

        except Exception as e:
            logging.error(f"調整持倉失敗: {e}")
            return None
        
    def update_data_dict(self, position_today, position_acc):

        self.data_dict['datetime'] = self.datetime

        config_file_name = os.path.basename(os.environ['FUGLE_CONFIG_PATH'])
        self.data_dict['is_simulation'] = True if config_file_name == 'config.simulation.ini' else False

        current_portfolio = self.data_manager.update_current_portfolio_info_with_datetime(position_acc, self.datetime, 'current_portfolio.pkl')
        self.data_dict['current_portfolio_all'] = current_portfolio

        next_portfolio = self.data_manager.update_next_portfolio_info_with_datetime(position_today, self.datetime, 'next_portfolio.pkl')
        self.data_dict['next_portfolio_all'] = next_portfolio

        financial_summary = self.data_manager.update_financial_summary_with_datetime(self.acc, self.datetime, 'financial_summary.pkl')
        self.data_dict['financial_summary_all'] = financial_summary


        return self.data_dict

