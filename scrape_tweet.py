import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

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

def extract_tweet_data(tweet):
    try:
        text_element = WebDriverWait(tweet, 10).until(
            EC.presence_of_element_located((By.XPATH, './/div[@data-testid="tweetText"]'))
        )
        text = text_element.text
        
        timestamp_element = tweet.find_element(By.XPATH, './/a/time')
        tweet_link = timestamp_element.find_element(By.XPATH, '..').get_attribute('href')
        
        return {'tweetContent': text, 'tweetLink': tweet_link}
    except Exception as e:
        logging.error(f"Error extracting tweet data: {str(e)}")
        return None

def scrape_tweets(username, twitter_username, twitter_password):
    unique_tweets = {}
    url = f"https://twitter.com/{username}"
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(180)
        
        login_to_twitter(driver, twitter_username, twitter_password)
        
        driver.get(url)
        logging.info(f"Navigating to {url}")
        
        try:
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
        except TimeoutException:
            logging.warning("Timed out waiting for page to load")
            logging.info("Attempting to proceed anyway...")

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 20
        
        while scroll_attempts < max_scroll_attempts:
            tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            logging.info(f"Processing batch of {len(tweet_elements)} tweets")
            
            for tweet in tweet_elements:
                tweet_data = extract_tweet_data(tweet)
                if tweet_data and tweet_data['tweetLink'] not in unique_tweets:
                    if "Day" in tweet_data['tweetContent'] and "ML" in tweet_data['tweetContent']:
                        unique_tweets[tweet_data['tweetLink']] = tweet_data
            
            driver.execute_script("window.scrollBy(0, 5000);")
            time.sleep(3)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                logging.info(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}")
            else:
                scroll_attempts = 0
            last_height = new_height
            
            logging.info(f"Collected {len(unique_tweets)} unique matching tweets so far")
        
        if not unique_tweets:
            logging.warning("No tweets matching the criteria were found.")
        else:
            logging.info(f"Scraped a total of {len(unique_tweets)} unique matching tweets")
    except TimeoutException:
        logging.error("Page load timed out")
    except WebDriverException as e:
        logging.error(f"WebDriver error occurred: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
    finally:
        if driver:
            driver.quit()
    
    return list(unique_tweets.values())

def save_to_csv(tweets, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet', 'Link'])
        for tweet in tweets:
            writer.writerow([tweet['tweetContent'], tweet['tweetLink']])

username = ""
twitter_username = ""
twitter_password = ""
tweets = scrape_tweets(username, twitter_username, twitter_password)
save_to_csv(tweets, 'waterIsCoding.csv')

logging.info(f"Scraped {len(tweets)} tweets and saved them to waterIsCoding.csv")
