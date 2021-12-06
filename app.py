import config
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)  # Validates connection with API Keys

account = client.get_account()                      # Fetches Account balances

prices = client.get_symbol_ticker()                 # Fetches Coin prices

# EURtoUSD = client.get_ticker("EURUSDT")
EURtoUSD = client.get_symbol_ticker(symbol = "EURUSDT")
USDtoEUR = 1 / float(EURtoUSD["price"])


# Dictionaries for non-zero balances and their coin prices
myBalances = {}
myPrices = {}

 
def get_price(symbol, dictionary, USDEURconversion):
    """Saves current price of the parsed ticker symbol in euros to the provided dictionary"""
    try:
        currentPrice = client.get_symbol_ticker(symbol = f"{symbol}EUR")
        dictionary[symbol + "EUR"] = currentPrice["price"]
    except Exception as e:
        if e.message == "Invalid symbol.":
            try:
                currentPrice = client.get_symbol_ticker(symbol = f"{symbol}USDT")
                dictionary[symbol + "EUR"] = USDEURconversion * float(currentPrice["price"])
            except Exception as ee:
                print(ee.message) 
        else:
            print(e.message)


def get_total_balance(coins, prices):
    """Calculates the total account balance"""
    total = 0
    for coin in coins:
        if coin != "EUR":
            total += float(coins[coin]) * float(prices[coin + "EUR"])
        else:
            total += float(coins[coin])
    return total
        

# Saves non-zero balances in dictionary
for asset in account["balances"]:
    if float(asset["free"]) != 0:
        myBalances[asset["asset"]] = asset["free"]

# Saves current prices to dictionary
for coin in myBalances:
    if coin != "EUR":
        get_price(coin, myPrices, USDtoEUR)

get_total_balance(myBalances, myPrices)
