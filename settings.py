SQLALCHEMY_DATABASE_URI = 'sqlite:///../Data/SQLite/BuyTransactions.db'
SQLALCHEMY_BINDS = {
    'SellTransactions': 'sqlite:///../Data/SQLite/SellTransactions.db'
}
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = True
SQLALCHEMY_ECHO = False