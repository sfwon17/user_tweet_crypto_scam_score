# User_tweet_crypto_scam_score

This project involves analyzing tweet activity from specific users to assess their potential involvement in "pump and dump" schemes related to cryptocurrencies. It evaluates whether users are promoting and subsequently offloading tokens by examining tweet history, sentiment, and related metadata. In addition to analyzing token price trends to identify patterns consistent with pump-and-dump behavior, the project also considers overall market conditions for a more comprehensive assessment. The focus is on tokens with small market capitalizations (approximately $100 million). While it offers insights into potential market manipulation, it should not be used in isolation to definitively determine fraudulent behavior based solely on social media activity. This project was developed for personal use, with the primary objective of mitigating the risk of investing in tokens potentially manipulated by the observed users.
The system is designed to analyze a user's past tweets containing cryptocurrency tickers, assess their sentiment, and evaluate the performance of the associated token prices under varying market conditions. The process involves the following steps:

## How it Works
1. Scraping Tweets: Tweets are scraped from specific users on Twitter without the use of Twitter's official API.
2. Retrieving Metadata and Price History: Cryptocurrency metadata and historical price data are obtained through the CoinGecko API, which is freely available and does not require payment.
3. Sentiment Analysis: Natural Language Processing (NLP) techniques are applied to analyze the sentiment of each tweet mentioning a cryptocurrency ticker.
4. Scoring for Pump and Dump Risk: A score is calculated for each tweet, assessing the likelihood of a pump-and-dump scheme based on the tweet's sentiment, the performance of the cryptocurrency's price, and the prevailing market conditions at the time.
