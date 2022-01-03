from flask import Flask, render_template
from API_functions import get_my_balances, get_full_symbol_name, get_price, get_conversion

app = Flask(__name__)

# Runs before templates are rendered
# Passes values to base.html
@app.context_processor
def parse_to_base():
    coins = get_my_balances()
    return dict(coins=coins)


@app.route("/")
def index():
    coin_balances = get_my_balances()
    print(coin_balances)
    coin_prices = get_prices(coin_balances.keys())
    coin_values = {}
    print(coin_prices)
    for coin in coin_balances:
        calculated_value = coin_balances[coin] * coin_prices[coin]
        coin_values[coin] = f'{calculated_value:.8f} €' if calculated_value < 1 else f'{calculated_value:.2f} €'
        coin_prices[coin] = f'{coin_prices[coin]:.8f}'
        coin_balances[coin] = f'{coin_balances[coin]:11.8f}'
        #print(f"Values: {coin_values[coin]} Prices: {coin_prices[coin]} Balances: {coin_balances[coin]}")
    return render_template("index.html", coinBalances=coin_balances, coinPrices=coin_prices, coinValues=coin_values)

@app.route("/tutorial/")
def tutorial():
    return render_template("tutorial.html")

@app.route("/transactions")
def transactions():
    buy_transactions, sell_transactions = readToDataframes()
    return render_template("transactions.html", buyTransactions=[buy_transactions.to_html(classes='table-striped table-bordered table-sm', table_id="buyDataTable", header="true")])

@app.route("/crypto/<coin>/")
def coin_view(coin):
    coin_balances = get_my_balances()
    coin_balance = coin_balances[coin]
    coin_name = get_full_symbol_name(coin)
    coin_price = get_price(coin, get_conversion("USDtoEUR"))[coin]
    coin_value = float(coin_balance) * coin_price

    return render_template("coin_view.html",
        coin=coin,
        balance=f'{coin_balances[coin]:.8f} {coin}',
        coinName=coin_name,
        coinPrice=f'{coin_price:.8f} €' if coin_price < 0 else f'{coin_price:.2f} €',
        coinValue=f'{coin_value:.8f} €' if coin_value < 0 else f'{coin_value:.2f} €')

if __name__ == "__main__":
    app.run()