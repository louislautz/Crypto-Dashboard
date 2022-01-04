from flask_sqlalchemy import SQLAlchemy
from FlaskBackend import db

class Transactions(db.Model):
    """Parent class with all shared columns and get_or_create() function"""
    id = db.Column('Transaction ID', db.String(32), primary_key=True)
    coin = db.Column('Coin', db.String(8))
    currency = db.Column('Currency', db.String(8))
    final_amount = db.Column('Final Amount', db.Float())
    amount = db.Column('Amount', db.Float())
    fees = db.Column('Fees', db.Float())
    method = db.Column('Method', db.String(13))
    timestamp = db.Column('Timestamp', db.DateTime(), unique=True)

    def __init__(self, id, coin, currency, final_amount, amount, fees, method, timestamp):
        self.id = id
        self.coin = coin
        self.currency = currency
        self.final_amount = final_amount
        self.amount = amount
        self.fees = fees
        self.method = method
        self.timestamp = timestamp


class Buys(Transactions):
    """Specific Child class for buy transactions"""
    __tablename__= 'BuyTransactions'
    coins_left = db.Column('Coins Left', db.Float())

    def __init__(self, id, coin, currency, final_amount, amount, fees, method, timestamp, coins_left):
        super().__init__(id, coin, currency, final_amount, amount, fees, method, timestamp)
        self.coins_left = coins_left


class Sells(Transactions):
    """Specific Child class for sell transactions"""
    __bind_key__ = 'SellTransactions'
    __tablename__= 'SellTransactions'
    profit = db.Column('Profit', db.Float())

    def __init__(self, id, coin, currency, final_amount, amount, fees, method, timestamp, profit):
        super().__init__(id, coin, currency, final_amount, amount, fees, method, timestamp)
        self.profit = profit
