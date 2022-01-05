import config
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)  # Validates connection with API Keys

def get_conversion(selector):
    """Converts currencies. Return conversionrate"""
    euroToDollar = client.get_symbol_ticker(symbol = "EURUSDT")
    EURtoUSD = float(euroToDollar["price"])
    USDtoEUR = 1 / float(EURtoUSD)

    try:
        if selector == "USDtoEUR":
            return USDtoEUR
        elif selector == "EURtoUSD":
            return EURtoUSD
        else:
            raise ValueError(f"{selector} is not a valid conversion request! \n\
                Conversion requests must have the format CURtoCUR, where CUR are two different currencies")
    except ValueError as err:
        print(err)
 
 
def get_price(symbol, USDEURconversion):
    """Saves current price of the parsed ticker symbol in euros to the provided dictionary"""
    dictionary = {}
    try:
        currentPrice = client.get_symbol_ticker(symbol = f"{symbol}EUR")
        dictionary[symbol] = float(currentPrice["price"])
    except Exception as e:
        if e.message == "Invalid symbol.":
            try:
                currentPrice = client.get_symbol_ticker(symbol = f"{symbol}USDT")
                dictionary[symbol] = USDEURconversion * float(currentPrice["price"])
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
        else:
            myPrices.update({'EUR': 1})
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
    """Returns non-zero balances as dictionary"""
    myBalances = {}
    account = client.get_account()
    for asset in account['balances']:
        if float(asset["free"]) != 0:
            myBalances[f"{asset['asset']}"] = float(asset["free"])
    return myBalances


def get_full_symbol_name(coin="ALL"):
    """Returns a dictionary with the symbol as key and the full symbol name as value"""
    coins = get_my_balances()
    assets = client.get_margin_all_assets()
    names = {}
    for asset in assets:
        if asset['assetName'] in coins.keys():
            names[f"{asset['assetName']}"] = asset['assetFullName']

    if coin != "ALL":                           # Returns only one specified coin name when argument is passed
        try:
            return names[coin]
        except KeyError as err:
            print(f"{err} is not a valid coin symbol")      
    else:                                       # Returns all coin names
        return names