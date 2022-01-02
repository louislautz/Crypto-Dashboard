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
    return render_template("index.html")

@app.route("/tutorial/")
def tutorial():
    return render_template("tutorial.html")

@app.route("/transactions")
def transactions():
    return render_template("transactions.html")

@app.route("/crypto/<coin>/")
def coin_view(coin):
    coin_balances = get_my_balances()
    coin_balance = coin_balances[coin]
    coin_name = get_full_symbol_name(coin)
    coin_price = get_price(coin, get_conversion("USDtoEUR"))[coin+'EUR']
    coin_value = float(coin_balance) * coin_price

    return render_template("coin_view.html",
        coin=coin,
        balance=f'{coin_balances[coin]:.8f} {coin}',
        coinName=coin_name,
        coinPrice=f'{coin_price:.8f} €',
        coinValue=f'{coin_value:.8f} €')

if __name__ == "__main__":
    app.run()