import os
import requests
import logging
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
        # Get top story IDs
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
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        # Clean up and limit length to avoid massive prompts
        clean_text = ' '.join(text.split())[:3000] 
        return clean_text
    except Exception as e:
        logger.warning(f"Could not scrape {url}: {e}")
        return ""

import html

def generate_ai_briefing(stories):
    """Uses Google Gemini to summarize the stories into a morning briefing."""
    logger.info("Generating AI Briefing with Gemini...")
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not set."
        
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Use the specific 2.5-flash model available on your account
    model_name = 'gemini-2.5-flash-lite' 
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Ensure we use the full 'models/' prefix if required
        if 'models/gemini-2.5-flash-lite' in available_models:
            model_name = 'models/gemini-2.5-flash-lite'
        elif any('2.5-flash' in m for m in available_models):
            model_name = [m for m in available_models if '2.5-flash' in m][0]
            logger.info(f"Using discovered model: {model_name}")
    except Exception as e:
        logger.warning(f"Could not list models, defaulting to gemini-2.5-flash-lite. Error: {e}")

    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        return f"Error initializing model {model_name}: {e}"

    # Build a much better "Premium" prompt
    prompt = """
    You are an elite AI Tech Journalist. Create a high-end 'Morning Intelligence Briefing' based on the following Hacker News stories.
    
    STRICT FORMATTING RULES:
    1. Start with a bold header: 🚀 <b>TECH INTELLIGENCE BRIEFING</b>
    2. For each story, use a relevant emoji and a bold title.
    3. Include a short 'The Bottom Line' section for each story explaining the impact.
    4. Use <b>bold</b> and <i>italic</i> HTML tags for emphasis.
    5. Keep it punchy and professional.
    6. End with a short, inspiring 'Productivity Quote'.

    DATA FOR STORIES:
    """
    
    for i, story in enumerate(stories, 1):
        title = story.get('title', 'Unknown Title')
        url = story.get('url', 'No URL')
        content = scrape_article_text(url)
        
        prompt += f"\n--- Story {i} ---\n"
        prompt += f"Title: {title}\n"
        prompt += f"Context: {content}\n"
        
    prompt += "\nGenerate the final HTML-formatted briefing now:"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error with {model_name}: {e}")
        return f"Failed to generate AI summary: {e}"

def send_telegram_message(message):
    """Sends the final briefing to your Telegram chat."""
    logger.info("Sending briefing to Telegram...")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Missing Telegram credentials.")
        return
        
    # Escape HTML special characters to prevent "400 Bad Request"
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
        if response is not None:
            logger.error(f"Telegram Response: {response.text}")

def main():
    logger.info("Starting Morning Briefing Automation...")
    
    stories = get_top_hn_stories(limit=5)
    if not stories:
        logger.error("No stories found. Exiting.")
        return
        
    briefing_text = generate_ai_briefing(stories)
    send_telegram_message(briefing_text)

if __name__ == "__main__":
    main()
