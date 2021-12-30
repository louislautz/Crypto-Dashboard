import config
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)  # Validates connection with API Keys

def get_conversion(selector):
    """Converts currencies. Return conversionrate"""
    euroToDollar = client.get_symbol_ticker(symbol = "EURUSDT")
    EURtoUSD = float(euroToDollar["price"])
    USDtoEUR = 1 / float(EURtoUSD)

    if selector == "USDtoEUR":
        return USDtoEUR
    elif selector == "EURtoUSD":
        return EURtoUSD
    else:
        raise ValueError(f"{selector} is not a valid conversion request! \n\
            Conversion requests must have the format CURtoCUR, where CUR are two different currencies")
        
 
def get_price(symbol, USDEURconversion):
    """Saves current price of the parsed ticker symbol in euros to the provided dictionary"""
    dictionary = {}
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
    return dictionary


def get_prices(coins):
    """Returns a dictionary with all prices for the specified coins"""
    myPrices = {}
    for coin in coins:
        if coin != "EUR":
            myPrices.update(get_price(coin, get_conversion("USDtoEUR")))
    return myPrices


def get_account_balance():
    """Calculates the total account balance"""
    coins = get_my_balances()
    prices = get_prices(coins)
    total = 0
    for coin in coins:
        if coin != "EUR":
            total += float(coins[coin]) * float(prices[coin + "EUR"])
        else:
            total += float(coins[coin])
    return total
        

def get_my_balances():
    """Saves non-zero balances in dictionary"""
    myBalances = {}
    account = client.get_account()
    for asset in account['balances']:
        if float(asset["free"]) != 0:
            myBalances[f"{asset['asset']}"] = float(asset["free"])
    return myBalances
