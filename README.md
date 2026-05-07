# 🚀 SmartMorning-AI: Autonomous Morning Briefing Engine

An elite, autonomous intelligence system that ensures you start your day with the most critical tech insights, distilled by Gemini 2.5-Flash and delivered directly to your device.

## 🚀 The Problem
As an aspiring engineer, keeping up with the rapid pace of tech news (Hacker News, TechCrunch, etc.) can be a 30-minute daily distraction. I built this to reclaim that time.

## 🧠 How it Works
This project is a **Full-Stack Automation Pipeline**:
1.  **Data Ingestion:** A Python script connects to the Hacker News API to identify the top 5 trending stories.
2.  **Web Scraping:** It dynamically scrapes the article content from the source URLs using `BeautifulSoup4`.
3.  **AI Synthesis:** The raw text is passed to the **Google Gemini 2.5-Flash** model. The AI synthesizes multiple long-form articles into a single, high-signal "Intelligence Briefing."
4.  **Autonomous Delivery:** The briefing is formatted into HTML and pushed to my Telegram via the Telegram Bot API.
5.  **Linux Daemon:** The entire process is scheduled as a background `cron` job to run autonomously every morning at 8:00 AM.

## 🛠️ Tech Stack
- **Language:** Python 3
- **AI Model:** Google Gemini 2.5-Flash (LLM)
- **APIs:** Telegram Bot API, Hacker News API
- **Libraries:** `requests`, `beautifulsoup4`, `google-generativeai`, `python-dotenv`
- **Infrastructure:** Linux Crontab (Automation)

## 📦 Setup & Deployment
1.  **Local Setup:** `pip install -r requirements.txt` and fill the `.env` file.
2.  **Serverless Automation (GitHub Actions):** 
    - Push this code to a GitHub Repository.
    - Go to **Settings > Secrets and Variables > Actions**.
    - Add three secrets: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`.
    - The system will now run automatically every morning at 8:00 AM IST!

---
*Built for the PainMed-PA Engineering Internship Application.*
