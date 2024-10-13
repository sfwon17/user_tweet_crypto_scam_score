import pandas as pd
import re
from transformers import pipeline
from datetime import datetime
import json

# loop through each rows and extract ticker
def extract_token_symbols(text):
    symbols = re.findall(r'\$[A-Za-z]+', text)
    return symbols[0] if len(symbols) == 1 else '' # only return token symbol if they mentioned only 1 token

def get_sentiment(text):
    try:
        result = sentiment_task(text)[0]
        return result['label'], result['score']
    except Exception as e:
        print(f"Error processing text: {e}")
        return 'ERROR', 0.0

def load_config(json_file):
    with open(json_file, 'r') as file:
        config = json.load(file)
    return config


tweets = pd.read_csv('scraped_tweets.csv')
config = load_config('config.json')
model_path = config['model_path'] # replace with your own NLP model
sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)

# convert the timestamp to date only
tweets['date'] = pd.to_datetime(tweets['timestamp']).dt.date
tweets['token_symbol'] = tweets ['text'].apply(extract_token_symbols)
tweets_filtered = tweets[tweets['token_symbol'] != ''] # remove empty token

# only include table 2 months before current date
current_date = config['cut_off_date']
tweets_filtered = tweets_filtered[tweets_filtered['date'] < datetime.strptime(current_date, "%Y-%m-%d").date()]

# Initialize lists to store results
sentiments = []
confidences = []

# Process each text in the DataFrame
for index, row in tweets_filtered.iterrows():
    sentiment, confidence = get_sentiment(row['text'])
    sentiments.append(sentiment)
    confidences.append(confidence)

# Add results to the DataFrame
tweets_filtered['sentiment'] = sentiments
tweets_filtered['confidence'] = confidences

# save
#tweets_filtered.to_csv("scraped_tweets_sentiment.csv", index=False)
