import json
import requests

####################################
# Variables
####################################
# ammount to invest
investment_in_euro = 304
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
investment_coins_options = {7: [], 10: [],
                            15: [], 20: [], 30: [], 60: [], 90: []}
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
                                    coin_staking_option["config"]["annualInterestRate"], coin_staking_option["config"]["maxPurchaseAmountPerUser"]])


############################################
# Print in tabular data format
############################################
for coin_data in cryptos_staking:
    # map the data to variables
    coin_name, locked_days, annual_interest, investment_constraint = coin_data

    # init the coin price to defaults
    coin_current_price_in_euro = usd_to_euro
    # check the current price of the coin
    if coin_name in cryptos_prices:
        coin_current_price_in_euro = round(float(
            cryptos_prices[coin_name][1])*float(usd_to_euro), 5)

    # for the given investment calculate:
    # the ammount of coins you buy with the investment
    bought_ammount_of_coins = round(float(investment_in_euro)/float(coin_current_price_in_euro), 2)
    # calculate the total ROI for the current based on the number of coin
    invested_ammount_of_coins = round(float(investment_constraint), 2) if float(investment_constraint) < float(bought_ammount_of_coins) else float(bought_ammount_of_coins)
    # the yearly profit
    interest_per_year_in_coins = float(annual_interest)*float(round(invested_ammount_of_coins))
    # the daily profit
    interest_per_day_in_coins = round(float(interest_per_year_in_coins/365), 4)
    interest_per_day_in_euro = round(float(interest_per_day_in_coins)*float(coin_current_price_in_euro), 2)

    # init elements for the investment coins options
    if int(locked_days) not in investment_coins_options:
        investment_coins_options.update({int(locked_days): []})

    # calculate the total ROI based on the coins that may be invested in the given investment duration (locked days)
    coin_roi_in_euro = round(float(interest_per_day_in_euro) * int(locked_days), 2)
    # classify the investment options based on the investment duration in days
    investment_coins_options.get(int(locked_days)).append(
        [coin_name, bought_ammount_of_coins, invested_ammount_of_coins, coin_current_price_in_euro, round(float(annual_interest)*100, 2), coin_roi_in_euro])

    # check if it belongs to most profitable coins
    if invested_ammount_of_coins > 1.0 and coin_roi_in_euro > 2.00:
        most_profitable_coins.append(
            [coin_name, invested_ammount_of_coins, locked_days, coin_roi_in_euro])

# Print all available coins to the corresponding duration
for k in investment_coins_options:
    print("\n---------------------------------------------------------------------------------------------------")
    print(k, " Days Investment. Found: ", len(
        investment_coins_options.get(k)), " coins.")
    print("---------------------------------------------------------------------------------------------------")
    print("{:<10} {:<25} {:<25} {:<25} {:<20} {:<20} {:<25}".format(
        'Coin', 'Total Investment (coins)', 'Allowed Investment (coins)', 'Duration (days)', 'Price (€)', 'APY (%)', 'ROI (€)'))
    for coin in sorted(investment_coins_options.get(k), key=lambda x: (float(x[4])), reverse=True):
        print("{:<10} {:<25} {:<25} {:<25} {:<20} {:<20} {:<25}".format(coin[0], coin[1], coin[2], int(k), coin[3], coin[4], coin[5]))


# Propose the top-X coins in terms of monthly-interests
print("\n---------------------------------------------------------------------------------------------------")
print("Best coins with the highest profit based on investment duration")
print("---------------------------------------------------------------------------------------------------")
print("{:<10} {:<25} {:<20} {:<20}".format('Coin', 'Invested coins', 'Duration (days)', 'ROI (€)'))
for coin in sorted(most_profitable_coins, key=lambda x: (float(x[3])), reverse=True):
    print("{:<10} {:<25} {:<20} {:<20}".format(
        coin[0], coin[1], coin[2], coin[3]))
