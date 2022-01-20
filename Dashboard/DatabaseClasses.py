from datetime import datetime
import pandas as pd

# Internal Files
from .extensions import db


class Buys(db.Model):
    """Class for buy transactions"""
    __tablename__= 'BuyTransactions'

    coin = db.Column(db.String(8))
    currency = db.Column(db.String(8))
    final_amount = db.Column(db.Float())
    amount = db.Column(db.Float())
    coins_left = db.Column(db.Float())
    price = db.Column(db.Float())
    fees = db.Column(db.Float())
    method = db.Column(db.String(13))
    timestamp = db.Column(db.DateTime())
    id = db.Column(db.String(32), primary_key=True)

    def __init__(self, id, coin, currency, final_amount, amount, price, fees, method, timestamp, coins_left):
        self.id = id
        self.coin = coin
        self.currency = currency
        self.final_amount = final_amount
        self.amount = round(amount, 4)
        self.price = round(price, 2) if price > 1 else round(price, 5)
        self.fees = fees
        self.method = method
        self.timestamp = timestamp
        self.coins_left = coins_left


class Sells(db.Model):
    """Class for buy transactions"""
    __bind_key__ = 'SellTransactions'
    __tablename__= 'SellTransactions'

    coin = db.Column(db.String(8))
    currency = db.Column(db.String(8))
    final_amount = db.Column(db.Float())
    amount = db.Column(db.Float())
    profit = db.Column(db.Float())
    price = db.Column(db.Float())
    fees = db.Column(db.Float())
    method = db.Column(db.String(13))
    timestamp = db.Column(db.DateTime())
    id = db.Column(db.String(32), primary_key=True)

    def __init__(self, id, coin, currency, final_amount, amount, price, fees, method, timestamp, profit):
        self.id = id
        self.coin = coin
        self.currency = currency
        self.final_amount = final_amount
        self.amount = round(amount, 6)
        self.price = round(price, 2) if price > 1 else round(price, 5)
        self.fees = fees
        self.method = method
        datetimeObject = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y / %H:%M:%S')
        # print(f"\n\n\nObject: {datetimeObject}/ Type: {type(datetimeObject)}") TODO Fix datetime formatting
        self.timestamp = datetime.strptime(datetimeObject, '%d %b %Y / %H:%M:%S')
        # print(f"Object: {self.timestamp}/ Type: {type(self.timestamp)}\n\n\n")
        self.profit = round(profit, 2)

    def __repr__(self):
        return f"id: {self.id}, profit: {self.profit}"
    
