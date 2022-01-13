SQLALCHEMY_DATABASE_URI = 'sqlite:///../Data/SQLite/BuyTransactions.sqlite3'
SQLALCHEMY_BINDS = {
    'SellTransactions': 'sqlite:///../Data/SQLite/SellTransactions.sqlite3'
}
SQLALCHEMY_TRACK_MODIFICATIONS = False

DEBUG = True
SQLALCHEMY_ECHO = True