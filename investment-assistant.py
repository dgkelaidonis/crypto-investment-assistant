import json
import requests

####################################
# Variables
####################################
# ammount to invest
investment_in_euro = 200
# URL from 'floatrates.com' to get exchange data
usd_exchange_rates_url = "http://www.floatrates.com/daily/usd.json"
# URL to fetch the USDT/€ price from coinbace.com platform.
usdt_price_coinbase_url = "https://www.coinbase.com/api/v2/assets/prices/b26327c1-9a34-51d9-b982-9b29e6012648?base=EUR"
# URL to fetch the BTC/€ price from coinbace.com platform.
btc_price_coinbase_url = "https://www.coinbase.com/api/v2/assets/prices/5b71fc48-3dd3-540c-809b-f8c94d0e68b5?base=EUR"
# URL to fetch Coins' Prices
binance_prices_url = "https://www.binance.com/bapi/composite/v1/public/marketing/symbol/list"
# URL to fetch POS interests
binance_pos_url = "https://www.binance.com/bapi/earn/v1/friendly/pos/union?pageSize=200&status=SUBSCRIBABLE"
# Other variables
coins_30 = []
coins_60 = []
coins_90 = []
most_profitable_coins = []


##################################
# Coinbase cryptos' current prices
##################################
usd_to_euro = float(requests.get(usd_exchange_rates_url).json()["eur"]["rate"])
usdt_price = float(requests.get(usdt_price_coinbase_url).json()[
                   "data"]["prices"]["latest"])
btc_price = float(requests.get(btc_price_coinbase_url).json()
                  ["data"]["prices"]["latest"])
print()
print("---------------------------------------------------------------------------------------------------------------------")
print("Investment=", investment_in_euro, "€ | ", float(
    round(investment_in_euro/usd_to_euro, 2)), "$")
print("1€=", float(round(1/usd_to_euro, 2)), "$ | BTC=",
      btc_price, "€ | USDT=", usdt_price, "€")
print("---------------------------------------------------------------------------------------------------------------------")


##################################
# Binance Coins' prices
##################################
# coin price data
cryptos_prices = {}
# Binance coins prices dataset
binance_coins_prices_json_data = requests.get(binance_prices_url).json()
# iterate on bincance price data
for price_data in binance_coins_prices_json_data["data"]:
    # Add data on dictionary in form of coin_name: [coin_equivalent, coin_price, price_unit]
    cryptos_prices[price_data["name"]] = [price_data["symbol"], price_data["price"],
                                          price_data["symbol"].replace(price_data["name"], "").strip()]

##################################
# Binance Staking
##################################
# coin staking data
cryptos_staking = []
# Binance staking coins dataset
binance_json_data = requests.get(binance_pos_url).json()
# Iterate on available coins
for coin in binance_json_data["data"]:
    # Iterate on available staking options of the current coin.
    for coin_staking_option in coin["projects"]:
        # Get only available staking options
        if coin_staking_option["sellOut"] == False:
            # [coin_name, coin_current_value, annual_interest_%, locked_in_days]
            cryptos_staking.append([coin["asset"], coin_staking_option["duration"],
                                    coin_staking_option["config"]["annualInterestRate"]])


############################################
# Print in tabular data format
############################################
for coin_data in cryptos_staking:
    # map the data to variables
    coin_name, locked_days, annual_interest = coin_data

    # init the coin price to defaults
    coin_current_price_in_euro = usd_to_euro
    # check the current price of the coin
    if coin_name in cryptos_prices:
        coin_current_price_in_euro = round(float(
            cryptos_prices[coin_name][1])*float(usd_to_euro), 5)

    # for the given investment calculate:
    # the ammount of coins you buy with the investment
    ammount_of_coins = round(
        float(investment_in_euro)/float(coin_current_price_in_euro), 2)
    # the yearly profit (coins)
    interest_per_year = float(
        annual_interest)*float(round(ammount_of_coins))
    # the daily profit (coins)
    interest_per_day_coin = interest_per_year/365
    interest_per_day_euro = round(
        float(interest_per_day_coin*coin_current_price_in_euro), 5)
    # the monthly profit (coins)
    interest_per_month_coin = round(float(interest_per_day_coin*30), 4)
    interest_per_month_euro = round(
        float(interest_per_month_coin*coin_current_price_in_euro), 5)

    # classify coins per locked days
    if int(locked_days) == 30:
        coins_30.append([coin_name, ammount_of_coins, interest_per_month_euro,
                         coin_current_price_in_euro, round(float(annual_interest)*100, 2)])
    elif int(locked_days) == 60:
        coins_60.append([coin_name, ammount_of_coins, interest_per_month_euro,
                         coin_current_price_in_euro, round(float(annual_interest)*100, 2)])
    elif int(locked_days) == 90:
        coins_90.append([coin_name, ammount_of_coins, interest_per_month_euro,
                         coin_current_price_in_euro, round(float(annual_interest)*100, 2)])

    # check if it belongs to most profitable coins
    if ammount_of_coins > 100.0 and interest_per_month_euro > 3.00:
        most_profitable_coins.append(
            [coin_name, ammount_of_coins, interest_per_month_euro, locked_days])


# Clasify the coins per locked based on profit #coins vs. monthly interest
# Coins for 30 days lock
print()
print("---------------------------------------------------------------------------------------------------")
print("30 Days Investment. Found: ", len(coins_30), " coins.")
print("---------------------------------------------------------------------------------------------------")
print("{:<10} {:<25} {:<20} {:<20} {:<25}".format('Coin', 'Number of bought coins',
      'Monthly profit (€)', 'Price (€)', 'Annual Interest (%)'))
for coin in sorted(coins_30, key=lambda x: (float(x[1]), float(x[2])), reverse=True):
    print("{:<10} {:<25} {:<20} {:<20} {:<25}".format(
        coin[0], coin[1], coin[2], coin[3], coin[4]))

# Coins for 60 days lock
print()
print("---------------------------------------------------------------------------------------------------")
print("60 Days Investment. Found: ", len(coins_60), " coins.")
print("---------------------------------------------------------------------------------------------------")
print("{:<10} {:<25} {:<20} {:<20} {:<25}".format('Coin', 'Number of bought coins',
      'Monthly profit (€)', 'Price (€)', 'Annual Interest (%)'))
for coin in sorted(coins_60, key=lambda x: (float(x[1]), float(x[2]))):
    print("{:<10} {:<25} {:<20} {:<20} {:<25}".format(
        coin[0], coin[1], coin[2], coin[3], coin[4]))

# Coins for 60 days lock
print()
print("---------------------------------------------------------------------------------------------------")
print("90 Days Investment. Found: ", len(coins_90), " coins.")
print("---------------------------------------------------------------------------------------------------")
print("{:<10} {:<25} {:<20} {:<20} {:<25}".format('Coin', 'Number of bought coins',
      'Monthly profit (€)', 'Price (€)', 'Annual Interest (%)'))
for coin in sorted(coins_90, key=lambda x: (float(x[1]), float(x[2]))):
    print("{:<10} {:<25} {:<20} {:<20} {:<25}".format(
        coin[0], coin[1], coin[2], coin[3], coin[4]))


# Propose the best 3 coins in terms of #bought-coins vs. monthly-interests
print("\n---------------------------------------------------------------------------------------------------")
print("Most profitable coins to invest")
print("---------------------------------------------------------------------------------------------------")
print("{:<10} {:<25} {:<20}".format('Coin', 'Number of bought coins', 'Monthly profit (€)', 'Investment Days'))
for coin in sorted(most_profitable_coins, key=lambda x: (float(x[1]), float(x[2])), reverse=True):
    print("{:<10} {:<25} {:<20}".format(coin[0], coin[1], coin[2], coin[3]))
