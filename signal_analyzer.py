import pandas as pd

class SignalAnalyzer:
    def __init__(self, signal_df):
        self.signal_df = signal_df

    def get_daily_changes(self, date):
        if date not in self.signal_df.index:
            raise ValueError("The specified date is not available in the signal DataFrame.")
        
        # 將訊號向前移動一天，以反映實際交易發生的日期
        positions = self.signal_df.shift(1).astype(bool)
        
        #確保資料為布林類型
        current_positions = positions.loc[date].astype(bool)
        previous_positions = positions.shift(1).loc[date].astype(bool)
        
        # 新買入的股票：當天持有且前一天未持有
        buys = current_positions & ~previous_positions
        # 賣出的股票：前一天持有且當天未持有
        sells = ~current_positions & previous_positions
        # 繼續持有的股票：當天持有且前一天也持有
        holds = current_positions & previous_positions
        
        return {
            'buys': list(buys[buys].index),
            'sells': list(sells[sells].index),
            'holds': list(holds[holds].index)
        }

    def remove_never_bought_stocks(self):
        # 使用字典先收集所有有效的列
        valid_columns = {stock: self.signal_df[stock]
                         for stock in self.signal_df.columns
                         if self.signal_df[stock].any()}

        # 一次性使用 pd.concat 建立一個新的 DataFrame
        clean_df = pd.concat(valid_columns, axis=1)
        
        # 重新設定索引，以保持與原始signal_df相同的索引
        clean_df = clean_df.reindex(self.signal_df.index)

        return clean_df


