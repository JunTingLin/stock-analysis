from decimal import Decimal
from finlab.online.enums import *
from finlab.online.order_executor import OrderExecutor
from finlab.online.order_executor import calculate_price_with_extra_bid
import numbers
import logging

def patched_execute_orders(self, orders, market_order=False, best_price_limit=False, view_only=False, extra_bid_pct=0):
        """產生委託單，將部位同步成 self.target_position
        預設以該商品最後一筆成交價設定為限價來下單
        
        Attributes:
            orders (list): 欲下單的部位，通常是由 `self.generate_orders` 產生。
            market_order (bool): 以類市價盡量即刻成交：所有買單掛漲停價，所有賣單掛跌停價
            best_price_limit (bool): 掛芭樂價：所有買單掛跌停價，所有賣單掛漲停價
            view_only (bool): 預設為 False，會實際下單。若設為 True，不會下單，只會回傳欲執行的委託單資料(dict)
            extra_bid_pct (float): 以該百分比值乘以價格進行追價下單，如設定為 0.05 時，將以當前價的 +(-)5% 的限價進買入(賣出)，也就是更有機會可以成交，但是成交價格可能不理想；
                假如設定為 -0.05 時，將以當前價的 -(+)5% 進行買入賣出，也就是限價單將不會立即成交，然而假如成交後，價格比較理想。參數有效範圍為 -0.1 到 0.1 內。
        """

        if [market_order, best_price_limit, bool(extra_bid_pct)].count(True) > 1:
            raise ValueError("Only one of 'market_order', 'best_price_limit', or 'extra_bid_pct' can be set.")
        if extra_bid_pct < -0.1 or extra_bid_pct > 0.1:
            raise ValueError("The extra_bid_pct parameter is out of the valid range 0 to 0.1")

        self.cancel_orders()
        stocks = self.account.get_stocks(list({o['stock_id'] for o in orders}))

        pinfo = None
        if hasattr(self.account, 'get_price_info'):
            pinfo = self.account.get_price_info()

        # make orders
        for o in orders:

            if o['quantity'] == 0:
                continue

            if o['stock_id'] not in stocks:
                logging.warning(o['stock_id'] + 'not in stocks... skipped!')
                continue

            stock = stocks[o['stock_id']]
            action = Action.BUY if o['quantity'] > 0 else Action.SELL
            price = stock.close if isinstance(stock.close, numbers.Number) else (
                    stock.bid_price if action == Action.BUY else stock.ask_price
                    )

            if extra_bid_pct != 0:
                price = calculate_price_with_extra_bid(price, extra_bid_pct if action == Action.BUY else -extra_bid_pct)

            if pinfo and o['stock_id'] in pinfo:
                limitup = float(pinfo[o['stock_id']]['漲停價'])
                limitdn = float(pinfo[o['stock_id']]['跌停價'])
                price = max(price, limitdn)
                price = min(price, limitup)
            else:
                logging.warning('No price info for stock %s', o['stock_id'])

            if isinstance(price, Decimal):
                price = format(price, 'f')

            if best_price_limit:
                price_string = 'LOWEST' if action == Action.BUY else 'HIGHEST'
            elif market_order:
                price_string = 'HIGHEST' if action == Action.BUY else 'LOWEST'
            else:
                price_string = str(price)

            extra_bid_text = ''
            if extra_bid_pct > 0:
                extra_bid_text = f'with extra bid {extra_bid_pct*100}%'

            # logger.warning('%-11s %-6s X %-10s @ %-11s %s %s', action, o['stock_id'], abs(o['quantity']), price_string, extra_bid_text, o['order_condition'])
            # use print f-string format instead of logger
            action_str = 'BUY' if action == Action.BUY else 'SELL'
            order_condition_str = 'CASH' if o['order_condition'] == OrderCondition.CASH else 'MARGIN_TRADING' if o['order_condition'] == OrderCondition.MARGIN_TRADING else 'SHORT_SELLING' if o['order_condition'] == OrderCondition.SHORT_SELLING else 'DAY_TRADING_LONG' if o['order_condition'] == OrderCondition.DAY_TRADING_LONG else 'DAY_TRADING_SHORT' if o['order_condition'] == OrderCondition.DAY_TRADING_SHORT else 'UNKNOWN'
            
            # 替換原本的 print，使用 logger.info
            logging.info(f'{action_str:<11} {o["stock_id"]:10} X {round(abs(o["quantity"]), 3):<10} @ {price_string:<11} {extra_bid_text} {order_condition_str}')


            quantity = abs(o['quantity'])
            board_lot_quantity = int(abs(quantity // 1))
            odd_lot_quantity = int(abs(round(1000 * (quantity % 1))))

            if view_only:
                continue

            if self.account.sep_odd_lot_order():
                if odd_lot_quantity != 0:
                    self.account.create_order(action=action,
                                              stock_id=o['stock_id'],
                                              quantity=odd_lot_quantity,
                                              price=price, market_order=market_order,
                                              order_cond=o['order_condition'],
                                              odd_lot=True,
                                              best_price_limit=best_price_limit,
                                              )

                if board_lot_quantity != 0:
                    self.account.create_order(action=action,
                                              stock_id=o['stock_id'],
                                              quantity=board_lot_quantity,
                                              price=price, market_order=market_order,
                                              order_cond=o['order_condition'],
                                              best_price_limit=best_price_limit,
                                              )
            else:
                self.account.create_order(action=action,
                                          stock_id=o['stock_id'],
                                          quantity=quantity,
                                          price=price, market_order=market_order,
                                          order_cond=o['order_condition'],
                                          best_price_limit=best_price_limit,
                                          )
                
        return orders


# 替換原有的 execute_orders 方法
OrderExecutor.execute_orders = patched_execute_orders