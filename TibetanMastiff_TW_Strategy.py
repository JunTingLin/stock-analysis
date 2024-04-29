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

# ------- 交易下單 -------

from finlab.online.fugle_account import FugleAccount
import os
import configparser
import pandas as pd
from decimal import Decimal

config = configparser.ConfigParser()
config_file_name = 'config.simulation.ini'
config.read(config_file_name)

os.environ['FUGLE_CONFIG_PATH'] = config_file_name
os.environ['FUGLE_MARKET_API_KEY'] = config['FUGLE_MARKET']['FUGLE_MARKET_API_KEY']
acc = FugleAccount()

from finlab.online.order_executor import Position, OrderExecutor
# 每次策略資金都是當前帳戶的現金80%
fund = acc.get_cash() * 0.8
print(f"當前帳戶現金為{acc.get_cash()}")

# 獲取目前帳戶的持倉狀態
acc_position = acc.get_position()
print(f"當前帳戶持倉為{acc_position.position}")
current_ids = set(p['stock_id'] for p in acc_position.position)

# 獲取由report物件生成的今日持倉狀態
position_today = Position.from_report(report, fund, odd_lot=True)
new_ids = set(p['stock_id'] for p in position_today.position)

# 檢查是否acc_position持倉陣列是空的，例如初始狀態，帳戶股票部位都是空的狀況
if not acc_position.position:
    order_executor = OrderExecutor(position_today, account=acc)
    order_executor.create_orders()  # 調整到這個持倉


# 檢查今天是否為月初第一天，月初第一天確定換股調整
today = pd.Timestamp.now().normalize()  # 正規化以去除時間部分
# 判斷今天是否為月份至今的最後一個交易日
month_start = today.replace(day=1)
month_trading_days = close.loc[month_start:today].index

if not month_trading_days.empty:
    first_trading_day = month_trading_days.index[0]
    last_trading_day = month_trading_days.index[-1]
    if today == first_trading_day:
        print(f"今天是{today}，為該月實際的第一個交易日，將執行換股調整，於下一個交易日生效")
        # 如果今天是該月實際的第一個交易日，則執行換股調整
        position_today = Position.from_report(report, fund, odd_lot=True)
        order_executor = OrderExecutor(position_today, account=acc)
        order_executor.create_orders()  # 調整到這個持倉

    elif today == last_trading_day:
        # 如果今天和close的最後一個交易日相同，則判斷帳戶股票部位是否有要提前出售的(跌8%)
        remove_ids = current_ids - new_ids
        if remove_ids:
            print(f"今天是{today}，需要移除的股票有{remove_ids}，將於下一個交易日出售")
            # 為需要移除的股票設置數量為0，其它幾檔的數量維持不變
            for position in acc_position.position:
                if position['stock_id'] in remove_ids:
                    position['quantity'] = Decimal('0')

            order_executor = OrderExecutor(acc_position, account=acc)
            order_executor.create_orders()
        else:
            print(f"今天是{today}，沒有跌停的股票需要出售，不需要調整持倉")
    else:
        print(f"今天{today}是休市日")

else:
    print(f"今天{today}是休市")

    


# 刪除委託單
# order_executor.cancel_orders()

# 拿到當前帳戶的股票部位
# acc.get_position()



