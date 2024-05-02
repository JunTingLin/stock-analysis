class LineMessage:
    def __init__(self):
        self.cash = None
        self.positions_acc = []
        self.positions_next = []
        self.date = None
        self.message = ""
        self.error = ""

    def set_cash(self, cash):
        self.cash = cash

    def set_positions_acc(self, positions_acc):
        self.positions_acc = positions_acc

    def set_positions_next(self, positions_next):
        self.positions_next = positions_next

    def set_date(self, date):
        self.date = date

    def append_message(self, additional_message):
        if self.message and additional_message:
            self.message += "\n"
        self.message += additional_message

    def append_error(self, error_message):
        if self.error and error_message:
            self.error += "\n"
        self.error += error_message

    def __str__(self):
        return f"LineMessage: cash={self.cash}, positions_acc={self.positions_acc}, positions_next={self.positions_next}, date={self.date}, message={self.message}"
    
    def to_dict(self):
        return {
            'today': self.date,
            'cash': self.cash,
            'position_acc': self.positions_acc,
            'position_next': self.positions_next,  # 注意這裡要匹配模板中的變數名
            'message': self.message,
            'error': self.error
        }
