def calculate_portfolio_value(positions, close_prices):
    total_value = 0
    portfolio_details = []
    for position in positions:
        stock_id = position['stock_id']
        quantity = position['quantity']
        if stock_id in close_prices:
            close_price = close_prices[stock_id].iloc[-1]  # 取得最後一筆交易日的收盤價
            stock_value = close_price * float(quantity) *1000  # 將 Decimal 轉換為 float 進行計算
            total_value += stock_value
            portfolio_details.append({
                'stock_id': stock_id,
                'quantity': quantity,
                'close_price': close_price,
                'stock_value': stock_value
            })
    return total_value, portfolio_details
