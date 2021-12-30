from flask import Flask, render_template
from API_functions import get_my_balances

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

@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")

@app.route("/crypto/<coin>")
def coin_view(coin):
    return render_template("coin_view.html", coin=coin)

if __name__ == "__main__":
    app.run()