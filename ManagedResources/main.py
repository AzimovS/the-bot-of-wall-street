from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from portfolio import Stock, Portfolio

app = FastAPI()

@app.post("/add-stock")
def buy_stock(stock: Stock):
    portfolio.buy_stock(stock.symbol, stock.name)
    return {"message": f"Started tracking {stock.symbol}."}

@app.post("/remove-stock")
def sell_stock(stock: Stock):
    portfolio.sell_stock(stock.symbol, stock.name)
    return {"message": f"Stopped tracking {stock.shares}."}