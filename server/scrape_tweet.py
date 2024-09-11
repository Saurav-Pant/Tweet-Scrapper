import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USERNAME_TO_SCRAPE = "novasarc01"  
DESIRED_KEYWORDS = ["DAILY", "ML", "GRIND"]  
JSON_FILENAME = '../client/content/lambdaux.json'
MAX_TWEETS_TO_COLLECT = 1000  
SCROLL_PAUSE_TIME = 1  

def login_to_twitter(driver, username, password):
    login_url = "https://twitter.com/login"
    driver.get(login_url)
    
    try:
        logging.info("Waiting for username field...")
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
        )
        username_field.send_keys(username)
        logging.info("Username entered")
        
        logging.info("Clicking Next button...")
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
        )
        next_button.click()
        
        logging.info("Waiting for password field...")
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
        )
        password_field.send_keys(password)
        logging.info("Password entered")
        
        logging.info("Clicking Log in button...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
        )
        login_button.click()
        
        logging.info("Waiting for main page to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
        )
        
        logging.info("Login successful")
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        logging.error(f"Current URL: {driver.current_url}")
        logging.error(f"Page source: {driver.page_source}")
        raise

def extract_tweet_data(tweet_element):
    try:
        tweet_text = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
    except Exception as e:
        logging.warning(f"Could not extract tweet text: {str(e)}")
        tweet_text = ""

    try:
        tweet_link = tweet_element.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute('href')
    except Exception as e:
        logging.warning(f"Could not extract tweet link: {str(e)}")
        tweet_link = ""

    if tweet_text or tweet_link:
        return {
            'tweetContent': tweet_text,
            'tweetLink': tweet_link
        }
    else:
        logging.warning("Skipping tweet due to missing content and link")
        return None

def scrape_recent_tweets(username, twitter_username, twitter_password):
    unique_tweets = {}
    url = f"https://twitter.com/{username}"
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        
        login_to_twitter(driver, twitter_username, twitter_password)
        
        driver.get(url)
        logging.info(f"Navigating to {url}")
        
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))

        last_height = driver.execute_script("return document.body.scrollHeight")
        while len(unique_tweets) < MAX_TWEETS_TO_COLLECT:
            tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            logging.info(f"Processing batch of {len(tweet_elements)} tweets")
            
            new_tweets_found = False
            for tweet in tweet_elements:
                tweet_data = extract_tweet_data(tweet)
                if tweet_data and tweet_data['tweetLink'] and tweet_data['tweetLink'] not in unique_tweets:
                    if all(keyword.lower() in tweet_data['tweetContent'].lower() for keyword in DESIRED_KEYWORDS):
                        unique_tweets[tweet_data['tweetLink']] = tweet_data
                        new_tweets_found = True
                        logging.info(f"Found matching tweet: {tweet_data['tweetContent'][:50]}...")

            if not new_tweets_found:
                logging.info("No new matching tweets found in this scroll, attempting to load more...")

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logging.info("Reached the end of the page or no more tweets are loading.")
                break
            last_height = new_height

            logging.info(f"Collected {len(unique_tweets)} unique matching tweets so far")

        logging.info(f"Finished collecting tweets. Total unique matching tweets: {len(unique_tweets)}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()
    
    return list(unique_tweets.values())

def update_json(new_tweets, json_filename):
    try:
        with open(json_filename, 'r', encoding='utf-8') as file:
            content = file.read()
            existing_data = json.loads(content) if content else []
    except FileNotFoundError:
        existing_data = []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {str(e)}. Initializing with empty list.")
        existing_data = []

    existing_links = set(item['Link'] for item in existing_data)

    updated_data = []
    for tweet in reversed(new_tweets):  
        if tweet['tweetLink'] not in existing_links:
            updated_data.append({
                "Tweet": tweet['tweetContent'],
                "Link": tweet['tweetLink']
            })
            existing_links.add(tweet['tweetLink'])

    updated_data.extend(existing_data)

    with open(json_filename, 'w', encoding='utf-8') as file:
        json.dump(updated_data, file, indent=2)

def daily_update():
    twitter_username = os.environ.get('TWITTER_USERNAME')
    twitter_password = os.environ.get('TWITTER_PASSWORD')

    if not all([twitter_username, twitter_password]):
        logging.error("Missing required environment variables. Please check your GitHub Actions secrets and environment variables.")
        return

    new_tweets = scrape_recent_tweets(USERNAME_TO_SCRAPE, twitter_username, twitter_password)
    update_json(new_tweets, JSON_FILENAME)

    logging.info(f"Daily update completed. Added {len(new_tweets)} new tweets.")

if __name__ == "__main__":
    daily_update()