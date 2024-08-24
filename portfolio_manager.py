from data_persistence_manager import DataPersistenceManager
from data_processor import DataProcessor
from finlab.online.order_executor import Position, OrderExecutor
import logging
from decimal import Decimal
import os


class PortfolioManager:
    def __init__(self, acc, fund, strategy_class_name, datetime, extra_bid_pct, log_filepath):
        self.acc = acc
        self.fund = fund
        self.strategy = self.load_strategy(strategy_class_name)
        self.datetime = datetime
        self.extra_bid_pct = extra_bid_pct
        self.log_filepath = log_filepath
        self.data_dict = {}
        self.data_processor = DataProcessor()
        self.data_persistence_manager = DataPersistenceManager()
        self.report = None
        self.position_acc = None
        self.position_today = None

    def load_strategy(self, strategy_class_name):
        if strategy_class_name == 'TibetanMastiffTWStrategy':
            from strategy_class.tibetanmastiff_tw_strategy import TibetanMastiffTWStrategy as strategy_class
        elif strategy_class_name == 'PeterWuStrategy':
            from strategy_class.peterwu_tw_strategy import PeterWuStrategy as strategy_class
        else:
            raise ValueError(f"Unknown strategy class: {strategy_class_name}")
        return strategy_class()
    
    def execute_order(self):
        self.report = self.strategy.run_strategy()
        self.position_acc = self.acc.get_position()
        self.position_today = Position.from_report(self.report, self.fund, odd_lot=True)
        self.position_today = self.rebalance_portfolio(self.position_today, self.position_acc)

        if self.position_today is not None:
            order_executor = OrderExecutor(self.position_today, account=self.acc)
            # order_executor.create_orders(extra_bid_pct=self.extra_bid_pct)

        
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
        
    def update_data_dict(self, report_directory):
        self.data_dict['datetime'] = self.datetime

        config_file_name = os.path.basename(os.environ['FUGLE_CONFIG_PATH'])
        self.data_dict['is_simulation'] = config_file_name == 'config.simulation.ini'

        # 保存 finlab 報告
        report_filename = f'{self.datetime.strftime("%Y-%m-%d_%H-%M-%S")}.html'
        report_save_path = os.path.join(report_directory, report_filename)
        self.data_persistence_manager.save_finlab_report(self.report, report_save_path)
        self.data_dict['finlab_report_path'] = report_save_path

        # 更新 current_portfolio_today
        current_portfolio = self.data_processor.process_current_portfolio(self.acc, self.position_acc, self.datetime)
        self.data_dict['current_portfolio_today'] = current_portfolio

        # 更新 next_portfolio_today
        next_portfolio = self.data_processor.process_next_portfolio(self.position_today, self.datetime)
        self.data_dict['next_portfolio_today'] = next_portfolio

        # 解析日誌並取得下單狀況
        order_status = self.data_processor.process_order_status(self.log_filepath)
        self.data_dict['order_status'] = order_status

        # 更新 financial_summary 並保存所有數據
        financial_summary = self.data_processor.process_financial_summary(self.acc, self.datetime)
        self.data_persistence_manager.save_financial_summary(financial_summary)
        self.data_dict['financial_summary_all'] = self.data_persistence_manager.load_financial_summary()

        return self.data_dict

