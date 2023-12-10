from pydantic import BaseModel

class Stock(BaseModel):
    symbol: str
    name: str

class Portfolio:
    def __init__(self):
        self.stocks = set()

    def add_stock(self, stock):
        self.stocks.add(stock)
    
    def remove_stock(self, stock):
        self.stocks.remove(stock)
    