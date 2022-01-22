# External Packages
import pandas as pd
import re
import os
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

EXCEL_DATA_LOCATION = 'Data/Excel/'


def sortMonths(month):
    """Sort function for sorting the months in getMonthsFromFile"""
    months = {"JAN":0, "FEB":1, "MAR":2, "APR":3, "MAY":4, "JUN":5, "JUL":6, "AUG":7, "SEP":8, "OCT":9, "NOV":10, "DEC":11 }
    return months[month]


def getFileNames():
    """Returns two lists with all buy or sell files"""
    onlyfiles = [f for f in listdir('Data/Excel/') if isfile(join('Data/Excel/', f))]
    sellFiles = [file for file in onlyfiles if file.find("Sell") != -1]
    buyFiles = [file for file in onlyfiles if file.find("Buy") != -1]
    return [buyFiles, sellFiles]


def getMonthsFromFiles(files):
    """Returns a list of months. [MAY, JUN, JUL, AUG]"""
    fileNames = []
    for file in files:
        try:
            filename = re.findall(r"_\w{3}_", file)[0]  # Saves pattern matching _JUN_ or _MAY_
            filename = filename.replace('_', '')        # Removes _
            fileNames.append(filename)                  # Saves month to list
        except IndexError as err:
            print(err)
    fileNames.sort(key=sortMonths)
    return fileNames


def readAllFiles(filelist):
    if len(filelist) > 1:
        dataframe = pd.read_excel(EXCEL_DATA_LOCATION + filelist[0])
        for file in filelist[1:]:
            next_file = pd.read_excel(EXCEL_DATA_LOCATION + file)
            dataframe = dataframe.append(next_file)
    elif len(filelist) == 1:
        dataframe = pd.read_excel(EXCEL_DATA_LOCATION + filelist[0])
    else:
        dataframe = pd.DataFrame()
        raise FileNotFoundError('No Transaction Files provided')
    return dataframe


def getSpentMoney():
    """Returns the total money spent from the Credit Card"""
    selection = db.session.query(Buys).filter(Buys.method == 'Credit Card').all()
    #selection = db.session.query(func.sum(Buys.amount)).filter(Buys.method == 'Credit Card').one()
    total = 0
    for item in selection:
        total += item.amount
    return total


def filterBySymbol(data, symbol):
    """Filters the dataframe by a certain symbol"""
    return data.loc[data['Coin'] == symbol]


def cleanBuyData(data):
    """Cleans up buy data"""

    # Format the remaining data
    data[['Amount', 'Currency']] = data['Amount'].str.split(' ', expand=True)
    data[['Final Amount', 'Coin']] = data['Final Amount'].str.split(' ', expand=True)

    data['Coins left'] = data['Final Amount']
    data['Coins left'] = data['Coins left'].astype(float)
    
    # Format common data
    new_data = cleanCommonData(data)

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
    data = data.rename(columns={"Date(UTC+2)": "Timestamp"})    # TODO Date(UTC+2) changes depending on where you download the Binance data from

    # Formatting and creating new columns
    data['Fees'] = data['Fees'].str.split(' ', expand=True)[0]
    data['Price'] = data['Price'].str.split(' ', expand=True)[0]
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])

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
    buyFiles, sellFiles = getFileNames()

    read_file = readAllFiles(buyFiles)
    read_file.to_csv (BUY_CSV_CONVERTED, index = None, header=True)
    read_file = readAllFiles(sellFiles)
    read_file.to_csv (SELL_CSV_CONVERTED, index = None, header=True)

    buy_df = pd.read_csv(BUY_CSV_CONVERTED)
    buy_df = cleanBuyData(buy_df)

    sell_df = pd.read_csv(SELL_CSV_CONVERTED)
    sell_df = cleanSellData(sell_df)

    buy_df, sell_df = FiFo(buy_df, sell_df)

    buy_df = rename_db_columns(buy_df)
    sell_df = rename_db_columns(sell_df)

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
    # fileDictionary = {}
    # buyFiles, sellFiles = getFileNames()
    # fileDictionary["buyFiles"] = getMonthsFromFiles(buyFiles)
    # fileDictionary["sellFiles"] = getMonthsFromFiles(sellFiles)
    # print(buyFiles, sellFiles)
    # print(fileDictionary)

    buy, sell = readToDataframes()

    buy_orders = []
    sell_orders = []

    for _, item in buy.iterrows():
        buyOrder = get_or_create(Buys, **get_db_kwargs(item))
        buy_orders.append(buyOrder)
    for _, item in sell.iterrows():
        sellOrder = get_or_create(Sells, **get_db_kwargs(item))
        sell_orders.append(sellOrder)

    db.session.commit()
