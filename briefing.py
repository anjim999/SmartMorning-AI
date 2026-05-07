import os
import requests
import logging
import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return ' '.join(text.split())[:2000] # Reduced context to save space
    except Exception as e:
        logger.warning(f"Could not scrape {url}: {e}")
        return ""

def generate_ai_briefing(stories):
    """Uses Google Gemini to summarize stories."""
    logger.info("Generating AI Briefing with Gemini...")
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not set."
        
    genai.configure(api_key=GEMINI_API_KEY)
    model_name = 'models/gemini-2.5-flash-lite'
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        return f"Error initializing model {model_name}: {e}"

    prompt = """
    You are an elite AI Tech Futurist. Create a 'Global Tech Intelligence Briefing' based on the following stories.
    
    STRICT RULES:
    1. Use ONLY these HTML tags: <b>, <i>, <a>. 
    2. Start with: <b>🌐 GLOBAL TECH INTELLIGENCE</b>
    3. Keep the TOTAL response under 3000 characters.
    4. For each story: Emoji + <b>TITLE</b> + 1-sentence summary + <i>Strategic Impact</i>.
    5. End with a 🧠 BRAIN FUEL quote.
    """
    
    for i, story in enumerate(stories, 1):
        prompt += f"\nStory {i}: {story.get('title')}\nContext: {scrape_article_text(story.get('url'))}\n"
        
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return f"Failed to generate AI summary: {e}"

def send_telegram_message(message):
    """Sends the final briefing to Telegram."""
    logger.info("Sending briefing to Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Missing Telegram credentials.")
        return
        
    # We don't use html.escape() on the WHOLE message because the AI is generating HTML tags.
    # Instead, we just ensure the message isn't empty or null.
    if not message:
        logger.error("Briefing message is empty.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"<b>🌅 Your AI Morning Tech Briefing</b>\n\n{message}",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
             logger.error(f"Telegram Error: {response.text}")
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
