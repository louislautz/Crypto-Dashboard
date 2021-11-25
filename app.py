import config
from binance.client import Client

client = Client(config.API_KEY, config.API_SECRET)

account = client.get_account()

print(client)
print(account)