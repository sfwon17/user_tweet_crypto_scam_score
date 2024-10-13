import pandas as pd
import numpy as np

# convert sentiment to a score
def sentiment_to_sentiment_score(filtered_data):
    conditions = [
        filtered_data['sentiment'] == 'negative',
        filtered_data['sentiment'] == 'neutral',
        filtered_data['sentiment'] == 'positive'
    ]

    # Define the corresponding sentiment values for each condition
    values = [0, 0.5, 1]

    # Use np.select() to assign sentiment values based on conditions
    filtered_data['sentiment_value'] = np.select(conditions, values, default=np.nan)
    return filtered_data

# calculate percentage change before tweet
def percentage_change_before_tweet_token(filtered_data):
    # for index, row in filtered_data.iterrows():
    #     # sentiment tweet
    #     sentiment_normalized = row['sentiment_value']/1
    #     # Before Tweet
    #     # change in token 30 days before
    #     delta_token_before = (row['price'] - row['price_before']) / row['price_before'] if row['price_before'] != 0 else 0
    #     delta_alt_before = (row['alt_price'] - row['alt_price_before']) / row['alt_price_before'] if row['alt_price_before'] != 0 else 0
    #
    #     # After tweet
    #     # change in token 30 days after
    #     delta_token_after = (row['price_after'] - row['price']) / row['price'] if row['price'] != 0 else 0
    #     delta_alt_after = (row['alt_price_after'] -row['alt_price']) / row['alt_price'] if row['alt_price'] != 0 else 0
    #
    #     # Calculate distances and opposite direction factors (ODF)
    #     # Before Tweet
    #     distance_before = abs(delta_token_before - delta_alt_before)
    #     ODF = 1 if delta_token_before * delta_alt_before < 0 else 0
    #     distance_adjusted_before = distance_before * (1 + ODF)
    #     distance_bounded_before = distance_adjusted_before / (distance_adjusted_before + 1) # Addded +1 to produce range of 0-1
    #
    #     # After Tweet
    #     distance_after = abs(delta_token_after - delta_alt_after)
    #     ODF = 1 if delta_token_after * delta_alt_after < 0 else 0
    #     distance_adjusted_after = distance_after * (1 + ODF)
    #     distance_bounded_after = distance_adjusted_after / (distance_adjusted_after + 1)
    #
    #     # Calculate the Scam Score
    #     scam_score = sentiment_normalized * (distance_bounded_before  + distance_bounded_after) / 2
    #
    #     # Ensure the Scam Score is between 0 and 1
    #     scam_score = max(0, min(scam_score, 1))
    for index, row in filtered_data.iterrows():
        # Normalized sentiment value
        sentiment_normalized = row['sentiment_value'] / 1  # If sentiment_value is already between 0 and 1

        # Before Tweet
        delta_token_before = (row['price'] - row['price_before']) / row['price_before'] if row['price_before'] != 0 else 0
        delta_alt_before = (row['alt_price'] - row['alt_price_before']) / row['alt_price_before'] if row['alt_price_before'] != 0 else 0

        # After Tweet
        delta_token_after = (row['price_after'] - row['price']) / row['price'] if row['price'] != 0 else 0
        delta_alt_after = (row['alt_price_after'] - row['alt_price']) / row['alt_price'] if row['alt_price'] != 0 else 0

        # Adjusted distances
        # Before Tweet
        distance_before = delta_token_before - delta_alt_before
        distance_adjusted_before = max(0, distance_before)
        distance_bounded_before = distance_adjusted_before / (distance_adjusted_before + 1)

        # After Tweet
        distance_after = delta_alt_after - delta_token_after
        distance_adjusted_after = max(0, distance_after)
        distance_bounded_after = distance_adjusted_after / (distance_adjusted_after + 1)

        # Calculate the Scam Score
        scam_score = sentiment_normalized * (distance_bounded_before + distance_bounded_after) / 2

        # Ensure the Scam Score is between 0 and 1
        scam_score = max(0, min(scam_score, 1))

        # Assign the scam_score back to the DataFrame if needed
        filtered_data.at[index, 'scam_score'] = scam_score

    return filtered_data

# read data
data = pd.read_csv('market_cap.csv')

# remove tickers with no price, this happens when token are just released/airdropped/available
data = data.dropna(subset=['price_before'])

# remove those with negative sentiment,
filtered_data = data[data['sentiment'].isin(['neutral', 'positive'])] # can also include negative but will return 0 score

# convert sentiment to score
filtered_data = sentiment_to_sentiment_score(filtered_data)

# find out scam score
filtered_data = percentage_change_before_tweet_token(filtered_data)

# save result
# filtered_data.to_csv("scam_score2.csv", index=False)