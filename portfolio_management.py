def calculate_portfolio_value(positions, close_prices, company_basic_info):
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
