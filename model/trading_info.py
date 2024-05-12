class TradingInfo:
    def __init__(self):
        self.data = {
            "is_simulation": True,
            "bank_cash_acc": 0,
            "positions_acc": [],
            "positions_cash_acc": 0,
            "total_cash": 0,
            "fund": 0,
            "positions_next": [],
            "today": None,
            "is_trading_day": True
        }

    def set_attribute(self, key, value):
        if key in self.data:
            self.data[key] = value
        else:
            raise KeyError(f"{key} is not a valid attribute of TradingInfo")
        

    
