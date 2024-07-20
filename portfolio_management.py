import logging

def get_current_portfolio_info(positions, close_prices, company_basic_info):
    total_value = 0
    portfolio_details = []
    
    for position in positions:
        stock_id = position['stock_id']
        quantity = float(position['quantity'])  # 將 quantity 統一轉型為 float

        if stock_id in close_prices:
            close_price = round(close_prices[stock_id].iloc[-1], 2)  # 取得最後一筆交易日的收盤價
            stock_value = int(close_price * quantity * 1000)
            total_value += stock_value

            # 查找公司簡稱
            stock_name = company_basic_info.loc[company_basic_info['stock_id'] == stock_id, '公司簡稱'].values[0]

            
            portfolio_details.append({
                'stock_id': stock_id,
                'stock_name': stock_name,
                'quantity': quantity,
                'close_price': close_price,
                'stock_value': stock_value
            })
    return total_value, portfolio_details

def get_next_portfolio_info(positions, company_basic_info):
    portfolio_details = []
    
    for position in positions:
        stock_id = position['stock_id']
        quantity = float(position['quantity'])  # 將 quantity 統一轉型為 float

        # 查找公司簡稱
        stock_name = company_basic_info.loc[company_basic_info['stock_id'] == stock_id, '公司簡稱'].values[0]

        
        portfolio_details.append({
            'stock_id': stock_id,
            'stock_name': stock_name,
            'quantity': quantity
        })
    return portfolio_details

def get_order_execution_info(warning_logs, company_basic_info):
    order_details = []

    for log in warning_logs:
        if ' - WARNING - ' in log and ' X ' in log and ' @ ' in log:
            try:
                parts = log.split(' - WARNING - ')[1].split()
                stock_id = parts[1]
                quantity = float(parts[3])
                limit_price = float(parts[5])

                stock_name = company_basic_info.loc[company_basic_info['stock_id'] == stock_id, '公司簡稱'].values[0]

                order_details.append({
                    'stock_id': stock_id,
                    'stock_name': stock_name,
                    'quantity': quantity,
                    'limit_price': limit_price
                })

                order_details = sorted(order_details, key=lambda x: x['stock_id'])
            except (IndexError, ValueError, KeyError) as e:
                logging.error(f"Error parsing log: {log}, Error: {e}")

    return order_details
