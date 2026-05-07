import os
import requests
import logging
import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_top_hn_stories(limit=5):
    """Fetches the top stories from Hacker News."""
    logger.info(f"Fetching top {limit} stories from Hacker News...")
    try:
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        response.raise_for_status()
        story_ids = response.json()[:limit]
        
        stories = []
        for story_id in story_ids:
            story_res = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            story_res.raise_for_status()
            stories.append(story_res.json())
            
        return stories
    except Exception as e:
        logger.error(f"Failed to fetch Hacker News: {e}")
        return []

def scrape_article_text(url):
    """Attempts to scrape the main text from an article URL."""
    if not url:
        return ""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return ' '.join(text.split())[:3000]
    except Exception as e:
        logger.warning(f"Could not scrape {url}: {e}")
        return ""

def generate_ai_briefing(stories):
    """Uses the modern Google GenAI library to summarize stories."""
    logger.info("Generating Ultra-Premium Briefing with Gemini...")
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not set."
        
    try:
        # Initialize the modern GenAI client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Build the prompt
        prompt = """
        You are an elite AI Tech Futurist and Lead Journalist at a top-tier tech newsletter. Create a 'Global Tech Intelligence Briefing' based on the following Hacker News data.
        
        TONE: Professional, insightful, and visionary.
        
        STRICT FORMATTING & STRUCTURE (HTML ONLY):
        1. HEADER: <b>🌐 GLOBAL TECH INTELLIGENCE</b>
        2. EXECUTIVE SUMMARY: A 2-sentence high-level overview of today's tech mood.
        3. THE STORIES:
           - Use a themed emoji for each story.
           - <b>STORY TITLE IN ALL CAPS</b>
           - A concise, high-signal summary.
           - <b>Strategic Impact:</b> <i>Why this matters for the future of the industry.</i>
        4. 🧠 BRAIN FUEL: A world-class productivity tip or a quote from a tech visionary.
        
        Use <b>bold</b> and <i>italic</i> tags generously.
        """
        
        for i, story in enumerate(stories, 1):
            prompt += f"\nStory {i}: {story.get('title')}\nContext: {scrape_article_text(story.get('url'))}\n"
            
        # Generate content using the new 2.0-flash model
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        return f"Failed to generate summary. Ensure your API Key is correct and has no extra spaces."

def send_telegram_message(message):
    """Sends the final briefing to Telegram."""
    logger.info("Sending briefing to Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Missing Telegram credentials.")
        return
        
    safe_message = html.escape(message)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"<b>🌅 Your AI Morning Tech Briefing</b>\n\n{safe_message}",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info("✅ Briefing sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

def main():
    logger.info("Starting Morning Briefing Automation...")
    stories = get_top_hn_stories(limit=5)
    if stories:
        briefing_text = generate_ai_briefing(stories)
        send_telegram_message(briefing_text)

if __name__ == "__main__":
    main()
