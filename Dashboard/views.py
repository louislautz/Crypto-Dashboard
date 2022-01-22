# External Packages
from flask import Blueprint, render_template, flash, redirect, url_for

# Internal Files
from .API_functions import *
from .database_functions import main, getSpentMoney 
from .databaseClasses import Sells, Buys
from .extensions import db

mainRoutes = Blueprint('mainRoutes', __name__)


# Runs before templates are rendered
# Passes values to base.html
@mainRoutes.context_processor
def parse_to_base():
    coins = get_my_balances()
    return dict(coins=coins)


@mainRoutes.route("/")
def index():
    total_money_spent = getSpentMoney()
    coin_balances = get_my_balances()
    coin_prices = get_prices(coin_balances.keys())
    coin_values = {}
    total_balance = 0
    for coin in coin_balances:
        calculated_value = coin_balances[coin] * coin_prices[coin]
        total_balance += calculated_value
        coin_values[coin] = f'{calculated_value:.8f} €' if calculated_value < 1 else f'{calculated_value:.2f} €'
        coin_prices[coin] = f'{coin_prices[coin]:.8f}'
        coin_balances[coin] = f'{coin_balances[coin]:11.8f}'
    return render_template("index.html", coinBalances=coin_balances, coinPrices=coin_prices, coinValues=coin_values, totalBalance=f'{total_balance:.2f} €', totalMoneySpent = total_money_spent)

@mainRoutes.route("/tutorial/")
def tutorial():
    return render_template("tutorial.html")

@mainRoutes.route("/buy_coin/")
def buy_coin():
    flash("This page is coming in Stage 2 of the project")
    return redirect(url_for('mainRoutes.index'))

@mainRoutes.route("/transactions")
def transactions():
    main()
    sell_orders = db.session.query(Sells)
    sell_keys = Sells.__table__.columns.keys()
    buy_orders = db.session.query(Buys)
    buy_keys = Buys.__table__.columns.keys()

    context = {}
    context.update({'sellOrders': sell_orders,
                    'sellKeys': sell_keys,
                    'buyOrders': buy_orders,
                    'buyKeys': buy_keys})

    return render_template("transactions.html", **context)

@mainRoutes.route("/crypto/<coin>/")
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