import csv
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

def login_to_twitter(driver, username, password):
    login_url = "https://twitter.com/login"
    driver.get(login_url)
    
    try:
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
        )
        username_field.send_keys(username)
        
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
        )
        next_button.click()
        
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
        )
        password_field.send_keys(password)
        
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
        )
        login_button.click()
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
        )
        
        logging.info("Login successful")
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        raise

def extract_tweet_data(tweet_element):
    try:
        tweet_text = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
        tweet_link = tweet_element.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute('href')
        return {
            'tweetContent': tweet_text,
            'tweetLink': tweet_link
        }
    except Exception as e:
        logging.error(f"Error extracting tweet data: {str(e)}")
        return None

def scrape_recent_tweets(username, twitter_username, twitter_password):
    unique_tweets = {}
    url = f"https://twitter.com/{username}"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
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

        scroll_attempts = 0
        max_scroll_attempts = 5  
        
        while scroll_attempts < max_scroll_attempts:
            tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            logging.info(f"Processing batch of {len(tweet_elements)} tweets")
            
            for tweet in tweet_elements:
                tweet_data = extract_tweet_data(tweet)
                if tweet_data and tweet_data['tweetLink'] not in unique_tweets:
                    if "Day" in tweet_data['tweetContent'] and "ML" in tweet_data['tweetContent']:
                        unique_tweets[tweet_data['tweetLink']] = tweet_data
            
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)
            
            scroll_attempts += 1
            logging.info(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}")
            
        logging.info(f"Collected {len(unique_tweets)} unique matching tweets")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()
    
    return list(unique_tweets.values())

def update_csv(new_tweets, csv_filename):
    existing_tweets = []
    existing_links = set()

    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  
            for row in reader:
                existing_tweets.append(row)
                existing_links.add(row[1])
    except FileNotFoundError:
        header = ['Tweet', 'Link']

    updated_tweets = []
    for tweet in reversed(new_tweets):  
        if tweet['tweetLink'] not in existing_links:
            updated_tweets.append([tweet['tweetContent'], tweet['tweetLink']])
            existing_links.add(tweet['tweetLink'])

    updated_tweets.extend(existing_tweets)

    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(updated_tweets)

def update_json(new_tweets, json_filename):
    try:
        with open(json_filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
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
    username = "wateriscoding"
    twitter_username = os.environ.get('TWITTER_USERNAME')
    twitter_password = os.environ.get('TWITTER_PASSWORD')
    csv_filename = 'waterIsCoding.csv'
    json_filename = '../client/WaterCodes.json'

    if not all([twitter_username, twitter_password]):
        logging.error("Missing required environment variables. Please check your .env file.")
        return

    new_tweets = scrape_recent_tweets(username, twitter_username, twitter_password)
    update_csv(new_tweets, csv_filename)
    update_json(new_tweets, json_filename)

    logging.info(f"Daily update completed. Added {len(new_tweets)} new tweets.")

if __name__ == "__main__":
    daily_update()
