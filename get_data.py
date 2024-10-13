import requests
import pandas as pd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_crypto_ticker():
    url = 'https://api.coingecko.com/api/v3/coins/list'
    ticker_list = requests.get(url)

    return ticker_list.json()

# find id based on symbol
def find_id_by_symbol(symbol, data):
    for entry in data:
        if entry['symbol'] == symbol:
            return entry['id']
    return None  # Return None if no match found

# find token id/name
def ticker_list(table, ticker_list):
    for index, row in table.iterrows():
        symbol = row['token_symbol'].split('$')[1]
        name = find_id_by_symbol(symbol, ticker_list)
        table.at[index, 'id'] = name

    return table

def get_price(ID,specific_date):
    url = f"https://api.coingecko.com/api/v3/coins/{ID}/history"
    params = {
        'date': str(specific_date)
    }
    time.sleep(15)
    try:
        response = requests.get(url, params=params)
        price = response.json()['market_data']['current_price']['usd']
    except:
        price =""

    return price

# find market data
def find_market_cap(table, ticker_list):
    for index, row in table.iterrows():
        print(row['id'])
        price = get_price(row['id'],datetime.strptime(row['date'], "%Y-%m-%d").strftime("%d-%m-%Y"))
        table.at[index, 'price'] = price

        # alt indicator, ETH price
        price = get_price("ethereum", datetime.strptime(row['date'], "%Y-%m-%d").strftime("%d-%m-%Y"))
        table.at[index, 'alt_price'] = price

        # price 30 days before
        one_month_before = (datetime.strptime(row['date'], "%Y-%m-%d") - relativedelta(days=2)).strftime("%d-%m-%Y") # convert to proper format
        price_before = get_price(row['id'],one_month_before)
        table.at[index, 'price_before'] = price_before

        # alt indicator, ETH price
        alt_price_before = get_price("ethereum",one_month_before)
        table.at[index, 'alt_price_before'] = alt_price_before

        # price 30 days after
        one_month_after = (datetime.strptime(row['date'], "%Y-%m-%d") + relativedelta(months=1)).strftime("%d-%m-%Y")
        price_after = get_price(row['id'], one_month_after)
        table.at[index, 'price_after'] = price_after

        # alt indicator, ETH price
        alt_price_after = get_price("ethereum", one_month_after)
        table.at[index, 'alt_price_after'] = alt_price_after

    return table

# read scrapped tweets
tweets_sentiment = pd.read_csv('scraped_tweets_sentiment.csv')
tweets_sentiment['token_symbol'] = tweets_sentiment['token_symbol'].str.lower()

# tickers list
tickers = get_crypto_ticker()

# find and extract official ticker based on coins mentioned
table = ticker_list(tweets_sentiment,tickers)

# extract data from coingecko api
table = find_market_cap(table, ticker_list)

# save
# table.to_csv("market_cap.csv", index=False)