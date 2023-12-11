class Portfolio:
    def __init__(self):
        self.stocks = set()

    def add_stock(self, stock):
        self.stocks.add(stock)
    
    def remove_stock(self, stock):
        self.stocks.remove(stock)
    