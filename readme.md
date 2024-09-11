
---

# Twitter Scraper Project

This project allows you to scrape tweets from a specific Twitter user that match certain keywords, save the data into a JSON file, and display them on a frontend application.

## Prerequisites

1. **Python**: Make sure Python is installed on your system.
2. **Chrome WebDriver**: Required for the Selenium script to work.
3. **Twitter Account**: You'll need a Twitter account to log in and scrape tweets.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Saurav-Pant/Tweet-Scrapper
cd Tweet-Scrapper
```

### 2. Set Up Python Environment

1. **Install Dependencies**:

   Navigate to the backend directory and install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:

   Change the `.env.example` file to `.env` and update the Twitter credentials:

   ```plaintext
   TWITTER_USERNAME=your_twitter_username
   TWITTER_PASSWORD=your_twitter_password
   ```

### 3. Run the Scraper Script

1. **Update the Username and Keywords**:

   Edit the `USERNAME_TO_SCRAPE` and `DESIRED_KEYWORDS` variables in the script to specify which user to scrape from and the keywords to filter the tweets.

   ```python
   USERNAME_TO_SCRAPE = "novasarc01"  # Change this to the Twitter username you want to scrape
   DESIRED_KEYWORDS = ["DAILY", "ML", "GRIND"]  # Keywords to filter tweets
   JSON_FILENAME = '../client/content/lambdaux.json'  # Path where scraped data will be saved
   ```

2. **Run the Script**:

   Execute the script to start scraping:

   ```bash
   python scrape_tweet.py
   ```

   The script will log in to Twitter, scrape the tweets that match the specified keywords, and save them into the JSON file.

### 4. Update the Frontend

1. **Modify JSON File Path**:

   In your frontend code, update the path to the JSON file where the tweets were saved. Typically, this will be in the `src/app/page.tsx` file:

   ```tsx
   // src/app/page.tsx
   import tweetsData from '../content/lambdaux.json';
   
   // Use tweetsData to display tweets on the UI
   ```

2. **Run the Frontend Application**:

   From the frontend directory, install dependencies and start the application:

   ```bash
   npm install
   npm run dev
   ```

3. **Access the Frontend**:

   Visit `http://localhost:3000` to see the tweets displayed on the UI.

### 5. Host the Frontend

Host the frontend using a service like Vercel, Netlify, or any other preferred hosting platform to make it accessible online.

## Additional Notes

- **Scroll Pause Time**: If the script is not finding enough tweets, consider adjusting the `SCROLL_PAUSE_TIME` variable to allow more time for tweets to load during scrolling.
- **Error Handling**: The script includes logging for debugging purposes. If you encounter issues, check the logs for detailed error messages.

---
