# External Packages
import pandas as pd
from os import listdir
from os.path import isfile, join
from sqlalchemy.orm.exc import NoResultFound

# Internal Files
from .databaseClasses import Buys, Sells
from .extensions import db


SELL_EXCEL_RAW_FILE = 'Data/Excel/Export Sell History.xlsx'
BUY_EXCEL_RAW_FILE = 'Data/Excel/Export Buy History.xlsx'
SELL_CSV_CONVERTED = 'Data/CSV/Sell.csv'
BUY_CSV_CONVERTED = 'Data/CSV/Buy.csv'
SELL_FULL_CSV_FILE = 'Data/CSV/Sell_Transactions.csv'
BUY_FULL_CSV_FILE = 'Data/CSV/Buy_Transactions.csv'


# sellFiles = []
# buyFiles = []
# onlyfiles = [f for f in listdir('Data/Excel/') if isfile(join('Data/Excel/', f))]
# for file in onlyfiles:
#     if file.find("Sell") != -1:
#         print(f"SELL: {file}")
#         sellFiles.append(file)
#     elif file.find("Buy") != -1:
#         print(f"BUY: {file}")
#         buyFiles.append(file)
#     else:
#         print("Invalid file")
# print(sellFiles, buyFiles)



def getSpentMoney(data):
    """Returns the total money spent from the Credit Card"""
    selection = data.loc[data['Method'] == "Credit Card"]
    return selection['Amount'].sum()


def filterBySymbol(data, symbol):
    """Filters the dataframe by a certain symbol"""
    return data.loc[data['Coin'] == symbol]


def cleanBuyData(data):
    """Cleans up buy data"""

    # Format the remaining data
    data[['Amount', 'Currency']] = data['Amount'].str.split(' ', expand=True)
    data[['Final Amount', 'Coin']] = data['Final Amount'].str.split(' ', expand=True)

    # Format common data
    new_data = cleanCommonData(data)

    new_data['Coins left'] = new_data['Final Amount']
    new_data['Coins left'] = new_data['Coins left'].astype(float)
    
    # Reordering columns
    new_data = new_data[['Coin', 'Final Amount', 'Coins left', 'Amount', 'Currency', 'Price', 'Fees', 'Timestamp', 'Method', 'Transaction ID']]
    return new_data


def cleanSellData(data):
    """Cleans up sell data"""

    # Format the remaining data
    data[['Amount', 'Coin']] = data['Amount'].str.split(' ', expand=True)
    data[['Final Amount', 'Currency']] = data['Final Amount'].str.split(' ', expand=True)
    data['Profit'] = 0.0

    # Format common data
    new_data = cleanCommonData(data)

    # Reordering columns
    new_data = new_data[['Final Amount', 'Currency', 'Amount', 'Coin', 'Profit', 'Price', 'Fees', 'Timestamp', 'Method', 'Transaction ID']]
    return new_data


def cleanCommonData(data):
    """Preforms data mutation thats common for sell AND buy data"""
    # Renaming
    data = data.rename(columns={"Date(UTC+1)": "Timestamp"})

    # Formatting and creating new columns
    data['Fees'] = data['Fees'].str.split(' ', expand=True)[0]
    data['Price'] = data['Price'].str.split(' ', expand=True)[0]
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%Y/%m/%d %H:%M:%S')

    # Changing column types
    data['Final Amount'] = data['Final Amount'].astype(float)
    data['Amount'] = data['Amount'].astype(float)
    data['Price'] = data['Price'].astype(float)
    data['Fees'] = data['Fees'].astype(float)
    return data


def recFiFo(sellOrder, buyList, currentSellAmount, indecesList ,listIndex=0):
    """Recursive helper function for FiFo. Fills in the 'Coins left' column and calculates profit"""
    currentBuyAmount = buyList.loc[indecesList[listIndex], 'Coins left']
    if currentSellAmount > currentBuyAmount:
        buyList.loc[indecesList[listIndex], 'Coins left'] = 0
        profit = currentBuyAmount * (sellOrder['Price'] - buyList.loc[indecesList[listIndex], 'Price']) # Calculates profit of current buyList entry
        return profit + recFiFo(sellOrder, buyList, currentSellAmount-currentBuyAmount, indecesList, listIndex+1)
    else:
        buyList.loc[indecesList[listIndex], 'Coins left'] = round(currentBuyAmount - currentSellAmount, 6)   # Handles a partial sell or a buy order
        profit = currentSellAmount * (sellOrder['Price'] - buyList['Price'][indecesList[listIndex]])
        return profit


def FiFo(buyData, sellData):
    """Custom First In First Out Algorithm. Returns profit"""

    # Iterates through all sell orders and groups them by coin
    for coin in set(sellData['Coin']):

        # Filters and sorts relevant data. Only used in loops to cut down runtime
        buys = filterBySymbol(buyData, coin).sort_values(by='Timestamp')
        sells = filterBySymbol(sellData, coin).sort_values(by='Timestamp')

        # Looping through both list
        for index, sell in sells.iterrows():
            # List comprehension to store indeces of buy orders that were bought before the sell order and are not fully sold yet
            boughtBefore = [i for i, buy in buys.iterrows() if (buy['Timestamp'] < sell['Timestamp'] and buyData.loc[i, 'Coins left'] != 0)]
            
            # pass boughtBefore to recursive function and selects correct entry from the whole dataframe
            if boughtBefore and sell['Profit'] == 0:
                sellData.loc[index, 'Profit'] = recFiFo(sell, buyData, sell['Amount'], boughtBefore)    # sets the profit of the current sell order
    
    return [buyData, sellData]


def readToDataframes():
    """Reads data files and returns cleaned data in dataframes"""
    # Convert xlsx to csv
    read_file = pd.read_excel(BUY_EXCEL_RAW_FILE)
    read_file.to_csv (BUY_CSV_CONVERTED, index = None, header=True)
    read_file = pd.read_excel(SELL_EXCEL_RAW_FILE)
    read_file.to_csv (SELL_CSV_CONVERTED, index = None, header=True)

    buy_df = pd.read_csv(BUY_CSV_CONVERTED)
    buy_df = cleanBuyData(buy_df)

    sell_df = pd.read_csv(SELL_CSV_CONVERTED)
    sell_df = cleanSellData(sell_df)

    buy_df, sell_df = FiFo(buy_df, sell_df)

    buy_df.to_csv(BUY_FULL_CSV_FILE)
    sell_df.to_csv(SELL_FULL_CSV_FILE)

    return [buy_df, sell_df]


def get_db_kwargs(item):
    """Returns a dictionary or key-value pairs for **kwargs"""
    dictionary = {}
    for key in item.keys():
        dictionary[key] = item[key]
    return dictionary


def rename_db_columns(dataframe):
    """Renames column in a dataframe to match with the database requirements"""
    dataframe = dataframe.rename(columns={
        "Timestamp": "timestamp",
        "Final Amount": "final_amount",
        "Currency": "currency",
        "Amount": "amount",
        "Coin": "coin",
        "Price": "price",
        "Fees": "fees",
        "Method": "method",
        "Transaction ID": "id"})
    if 'Profit' in dataframe:
        dataframe = dataframe.rename(columns={"Profit": "profit"})
    if 'Coins left' in dataframe:
        dataframe = dataframe.rename(columns={"Coins left": "coins_left"})
    return dataframe


def get_or_create(model, **kwargs):
    """Checks whether an entry is already in the databases and creates it if it is not"""
    instance = get_instance(model, **kwargs)
    if instance is None:
        instance = create_instance(model, **kwargs)

    return instance
    

def get_instance(model, **kwargs):
    """Returns first instance found"""
    try:
        return db.session.query(model).filter_by(id = kwargs['id']).first()
    except NoResultFound:
        return


def create_instance(model, **kwargs):
    """Creates an instance of the model"""
    try:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.flush()
    except Exception as msg:
        mtext = 'model:{}, args:{} => msg:{}'
        print(mtext.format(model, kwargs, msg))
        db.session.rollback()
        raise(msg)
    return instance



def main():
    buy, sell = readToDataframes()
    buy = rename_db_columns(buy)
    sell = rename_db_columns(sell)

    buy_orders = []
    sell_orders = []

    for _, item in buy.iterrows():
        buyOrder = get_or_create(Buys, **get_db_kwargs(item))
        buy_orders.append(buyOrder)
    for _, item in sell.iterrows():
        sellOrder = get_or_create(Sells, **get_db_kwargs(item))
        sell_orders.append(sellOrder)

    db.session.commit()
