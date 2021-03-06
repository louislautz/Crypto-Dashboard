from .Dashboard.API_functions import *

test_API_functions = False

if test_API_functions:
    conversion = get_conversion("USDtoEUR")

    print("\nget_converion() Tests: \n")

    print(get_conversion("USDtoEUR"))
    print(get_conversion("EURtoUSD"))
    print(get_conversion("DIGGA!"))


    print("\n\n get_price() Tests: \n")

    print(get_price("BTC", conversion))
    print(get_price("SAND", conversion))
    print(get_price("DIGGA", conversion))


    print("\n\n get_prices() Tests: \n")

    print(get_prices(["BTC", "BAT", "SAND", "ETH", "DIGGA"]))


    print("\n\n get_account_balance() Tests: \n")

    print(get_account_balance())


    print("\n\n get_my_balances() Tests: \n")

    print(get_my_balances())


    print("\n\n get_full_symbol_name() Tests: \n")

    print(get_full_symbol_name())
    print(get_full_symbol_name("BTC"))
    print(get_full_symbol_name("BAT"))
    print(get_full_symbol_name("DIGGA"))
