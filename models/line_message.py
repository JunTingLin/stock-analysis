class LineMessage:
    def __init__(self):
        self.cash = None
        self.positions_acc = []
        self.positions_next = []
        self.date = None
        self.message = None

    def set_cash(self, cash):
        self.cash = cash

    def set_positions_acc(self, positions_acc):
        self.positions_acc = positions_acc

    def set_positions_next(self, positions_next):
        self.positions_next = positions_next

    def set_date(self, date):
        self.date = date

    def set_message(self, message):
        self.message = message

    def __str__(self):
        return f"LineMessage: cash={self.cash}, positions_acc={self.positions_acc}, positions_next={self.positions_next}, date={self.date}, message={self.message}"
    
    def to_dict(self):
        return {
            'today': self.date,
            'cash': self.cash,
            'position_acc': self.positions_acc,
            'position_next': self.positions_next,  # 注意這裡要匹配模板中的變數名
            'msg': self.message
        }
