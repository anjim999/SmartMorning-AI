# 🌐 SmartMorning-AI: Autonomous Tech Intelligence Engine

**SmartMorning-AI** is a high-performance, autonomous agentic pipeline designed to distill global tech trends into actionable intelligence. Built for engineers and founders who value high-signal data with zero manual effort.

## 🚀 The Vision
In an era of information overload, the most valuable asset is time. **SmartMorning-AI** reclaims 30 minutes of your morning by autonomously identifying, scraping, and synthesizing the most critical stories from the global tech frontier.

## 🛠️ System Architecture
The engine operates as a multi-stage autonomous pipeline:
1.  **Ingestion:** Connects to the Hacker News API to retrieve top-tier trending items.
2.  **Web-Extraction:** Employs `BeautifulSoup4` with custom headers to bypass simple bot-protections and extract high-density article content.
3.  **Neural Synthesis:** Utilizes the **Gemini 2.5-Flash** LLM (via Google AI Studio) to perform deep semantic analysis. It doesn't just summarize—it analyzes **Strategic Impact**.
4.  **Delivery:** Formats the intelligence into a premium HTML briefing and pushes it to the user's Telegram via a dedicated bot interface.
5.  **Autonomous Scheduling:** Deployed via **GitHub Actions (Cron)** for serverless, 24/7 reliability, and locally via **Linux Systemd/Cron**.

## 🧬 Tech Stack
- **AI Core:** Google Gemini 2.5-Flash
- **Automation:** GitHub Actions (CI/CD / Scheduling)
- **Networking:** Telegram Bot API, HN Firebase API
- **Processing:** Python 3.x, Requests, BeautifulSoup4
- **Security:** Environment-based secret management (Dotenv / GitHub Secrets)

## 📦 Deployment & Automation
### 1. Local Execution
```bash
pip install -r requirements.txt
python briefing.py
```

### 2. Full Autonomy (GitHub Actions)
1.  Push code to a private or public GitHub Repository.
2.  Navigate to **Settings > Secrets and Variables > Actions**.
3.  Add the following secrets:
    - `GEMINI_API_KEY`: Your Google AI Studio Key.
    - `TELEGRAM_BOT_TOKEN`: Your Bot Token from @BotFather.
    - `TELEGRAM_CHAT_ID`: Your unique Telegram ID.
4.  The system will now autonomously deliver your briefing every day at 8:00 AM IST.

---
*Developed as a showcase of AI Orchestration and Automation for the PainMed-PA Engineering Internship.*
