import pandas as pd

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


def FiFo(buyData, sellData, symbol):
    """Custom First In First Out Algorithm. Returns profit"""
    # Filters and sorts relevant data. Only used in loops to cut down runtime
    buys = filterBySymbol(buyData, symbol).sort_values(by='Timestamp')
    sells = filterBySymbol(sellData, symbol).sort_values(by='Timestamp')

    # Looping through both list
    for index, sell in sells.iterrows():
        # List comprehension to store indeces of buy orders that were bought before the sell order and are not fully sold yet
        boughtBefore = [i for i, buy in buys.iterrows() if (buy['Timestamp'] < sell['Timestamp'] and buyData.loc[i, 'Coins left'] != 0)]
        
        # pass boughtBefore to recursive function and selects correct entry from the whole dataframe
        if boughtBefore and sell['Profit'] == 0:
            sellData.loc[index, 'Profit'] = recFiFo(sell, buyData, sell['Amount'], boughtBefore)    # sets the profit of the current sell order


def main():
    # Convert xlsx to csv
    read_file = pd.read_excel('Data/Excel/Export Buy History.xlsx')
    read_file.to_csv ('Data/CSV/Buy.csv', index = None, header=True)
    read_file = pd.read_excel('Data/Excel/Export Sell History.xlsx')
    read_file.to_csv ('Data/CSV/Sell.csv', index = None, header=True)

    buy_df = pd.read_csv('Data/CSV/Buy.csv')
    buy_df = cleanBuyData(buy_df)

    sell_df = pd.read_csv('Data/CSV/Sell.csv')
    sell_df = cleanSellData(sell_df)

    FiFo(buy_df, sell_df, 'BAT')
    FiFo(buy_df, sell_df, 'BTC')
    FiFo(buy_df, sell_df, 'ETH')


    for coin in set(sell_df['Coin']):
        test = sell_df.loc[sell_df['Coin']==coin]
        print(test)


    # coin_set = set(buy_df['Coin'])

    buy_df.to_csv('Data/CSV/Buy_Transactions.csv')
    sell_df.to_csv('Data/CSV/Sell_Transactions.csv')

    buySecondRound = pd.read_csv('Data/CSV/Buy_Transactions.csv', index_col=0)
    sellSecondRound = pd.read_csv('Data/CSV/Sell_Transactions.csv', index_col=0)

    FiFo(buySecondRound, sellSecondRound, 'BAT')
    FiFo(buySecondRound, sellSecondRound, 'BTC')
    FiFo(buySecondRound, sellSecondRound, 'ETH')

    # print(buySecondRound)
    # print(sellSecondRound)

if __name__ == '__main__':
    main()