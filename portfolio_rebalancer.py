import logging
from decimal import Decimal
from finlab.online.order_executor import OrderExecutor

def rebalance_portfolio(position_today, position_acc):
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