from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import logging
import re
import json

class TwitterScraper:
    def __init__(self, username, password, driver_path):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome(driver_path)

    def _input_username(self):
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
        )
        username_field.send_keys(self.username)
        username_field.send_keys(Keys.RETURN)

    def _input_password(self):
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        password_field.send_keys(self.password)
        password_field.send_keys(Keys.RETURN)

    def _input_unusual_activity(self):
        try:
            unusual_activity_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]'))
            )
            unusual_activity_field.send_keys(self.username)
            unusual_activity_field.send_keys(Keys.RETURN)
        except TimeoutException:
            # No unusual activity prompt, continue with login
            pass

    def login(self):
        logging.info("Start login process")
        try:
            self.driver.maximize_window()
            self.driver.get(TWITTER_LOGIN_URL)
            time.sleep(3)

            logging.info("Entering username...")
            self._input_username()
            logging.info("Username entered")

            logging.info("Checking for unusual activity prompt...")
            self._input_unusual_activity()
            logging.info("Unusual activity check complete")

            logging.info("Entering password...")
            self._input_password()
            logging.info("Password entered")

            print("Login Successful")
            #self.driver.get('https://twitter.com/QuantMeta')
        except Exception as e:
            print(f"Login Failed: {e}")

    def navigate_to_profile(self, username, num_tweets):
        logging.info(f"Navigating to profile: {username}")
        profile_url = f"https://twitter.com/{username}"
        tweets = []
        self.driver.get(profile_url)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="UserName"]'))
            )
            logging.info(f"Successfully loaded profile for {username}")
            # Start scraping tweets
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while len(tweets) < num_tweets:
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

                for tweet in tweet_elements:
                    if len(tweets) >= num_tweets:
                        break

                    try:
                        tweet_text = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]').text
                        timestamp = tweet.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
                        tweets.append({'text': tweet_text, 'timestamp': timestamp})
                        logging.info(f"Scraped tweet")
                    except NoSuchElementException:
                        logging.warning("Failed to extract.")

                # Scroll down to load more tweets
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new tweets to load

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            logging.info(f"Scraped {len(tweets)} tweets from {username}'s profile.")

        except TimeoutException:
            logging.error(f"Failed to load profile page for {username}")

        return tweets
    def close(self):
        self.driver.quit()
        logging.info("Browser closed")

def create_dataframe_and_csv(tweets, username):
    df = pd.DataFrame(tweets)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp', ascending=False)
    df = df.reset_index(drop=True)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{username}_tweets_{current_time}.csv"
    df.to_csv(filename, index=False)
    logging.info(f"Saved tweets to {filename}")
    return df

def clean_text(text):
    text = re.sub(r'\n', ' ', text)
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def load_config(json_file):
    with open(json_file, 'r') as file:
        config = json.load(file)
    return config

config = load_config('config.json')
TWITTER_LOGIN_URL = "https://twitter.com/login"

# login and scrape
scraper = TwitterScraper(config['login_username'], config['login_password'],config['driver_path'])
scraper.login()
scraped_tweets =scraper.navigate_to_profile(config['profile_to_visit'], config['num_tweets'])

# convert data to table
scraped_tweets = pd.DataFrame(scraped_tweets)
print(scraped_tweets)
scraped_tweets['timestamp'] = pd.to_datetime(scraped_tweets['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ')
scraped_tweets = scraped_tweets.sort_values('timestamp', ascending=False) # Sort by timestamp (most recent first)
scraped_tweets = scraped_tweets.reset_index(drop=True)
scraped_tweets['text'] = scraped_tweets['text'].apply(clean_text)

# save
#scraped_tweets.to_csv("scraped_tweets.csv", index=False)