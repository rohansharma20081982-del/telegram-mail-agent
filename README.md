Telegram AI Chat and Email Bot Agent

This is a Python-based Telegram bot that acts as an AI-powered chat assistant and email sender. It uses OpenAI's API for conversational AI, integrates with Google Sheets for dynamic data storage (e.g., configurations and logs), and sends emails via Gmail SMTP. The bot allows users to chat naturally, send polished emails based on text input, and logs activities for easy review.

Features

AI-Powered Chat: Engage in conversations with context-aware responses using OpenAI's GPT model.
Email Sending: Send emails to specified recipients with AI-refined content (e.g., polite rephrasing).
Google Sheets Integration: Store configurations (e.g., default emails) and logs (e.g., sent emails, chat history) in a Google Sheet for easy management and review.
User-Specific Conversations: Maintains chat history per user for coherent interactions.
Commands: Supports /start, /email, /clear, and more for control.
Security: Sensitive data (API keys) stored in a .env file; email data handled via secure Sheets.
Extensible: Built with modular code for easy customization.

Prerequisites

Python: Version 3.7 or higher.

Accounts/Services:

Telegram account (to create a bot via @BotFather).
OpenAI account (for API key).
Google account (for Sheets API).
Gmail account (for email sending, with 2FA enabled for app passwords).
Libraries: Install via pip (see Installation).
Hardware/Software: A computer with internet access; works on Windows, macOS, or Linux.

Installation

Clone or Download the Code: Save the provided Python script (e.g., telegram_ai_bot.py) to a folder.
Install Dependencies:

Copy code
pip install python-telegram-bot openai python-dotenv gspread google-auth google-auth-oauthlib google-auth-httplib2

Set Up Environment:

Create a .env file in the same folder with the following (replace placeholders):

Copy code

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
EMAIL_USER=your_gmail_address@gmail.com
EMAIL_PASS=your_gmail_app_password
TELEGRAM_BOT_TOKEN: Get from @BotFather (create a bot, copy the token).
OPENAI_API_KEY: From OpenAI platform (sign up, generate key).
EMAIL_USER: Your Gmail address.
EMAIL_PASS: Gmail app password (see setup below).
Setup
1. Telegram Bot
Message @BotFather on Telegram: /newbot, name it, get the token, and paste into .env.
2. OpenAI API
Sign up at OpenAI, create an API key, and add to .env.
3. Gmail for Emails
Enable 2FA on your Google account.
Generate an app password: Go to myaccount.google.com > Security > App passwords > Select "Mail" > "Other" > Generate. Use it in .env as EMAIL_PASS.
Note: For production, consider SendGrid instead of Gmail for better security.
4. Google Sheets for Data Storage
Create a Project: Go to Google Cloud Console, create a project (e.g., "TelegramBotProject").
Enable API: Search for "Google Sheets API" and enable it.
Create Service Account: Go to Credentials > Create Credentials > Service Account. Name it (e.g., "TelegramBotService"), set role to "Editor," download the JSON key file (e.g., telegram-bot-key.json), and save it in your project folder.

Create Google Sheet: Name it "TelegramBotData" (or update SPREADSHEET_NAME in code). Share it with the service account email (from JSON) as "Editor."
Set Up Tabs:
Config Tab: For settings (e.g., Row 1: "Key | Value"; Row 2: "DEFAULT_EMAIL | your_email@example.com").
Logs Tab: For activity logs (e.g., Row 1: "Timestamp | Action | Details").
Usage
Run the Bot:


Copy code
python telegram_ai_bot.py
The bot will start polling Telegram for messages.
Interact in Telegram:

Find your bot by username (from BotFather) and start chatting.
Use commands below.
Monitor Google Sheets:

Open "TelegramBotData" to view/edit configs or check logs in real-time.

Commands

/start: Initializes the bot and shows help. Clears/resets user history.
/email recipient@example.com Your message: Sends an AI-polished email to the recipient. If no recipient, sends conversation history to the default email from Sheets.
/clear: Clears the user's chat history and logs it.
Regular Messages: Chat with the bot for AI responses (e.g., "What's the weather?").
Example Interactions
User: /start → Bot: "Hello! ... Data is saved to Google Sheets!"
User: "Tell me a joke." → Bot: AI-generated joke.
User: /email friend@example.com Remind them about the meeting. → Bot: Sends polished email and logs to Sheets.
User: /email → Bot: Emails chat history to default address from Sheets.
File Structure
telegram_ai_bot.py: Main script.
.env: Environment variables (keep private).
telegram-bot-key.json: Google service account key (keep secure).
Google Sheet: "TelegramBotData" (online).
Troubleshooting
Bot Not Responding: Check Telegram token in .env and ensure bot is running.
OpenAI Errors: Verify API key and quota at OpenAI.
Email Not Sending: Confirm app password and Gmail settings. Check for "Less secure app access" if needed (temporary).
Sheets Errors: Ensure JSON key is correct, Sheet is shared, and API is enabled. Error: "access denied" → Re-share Sheet.
Common Issues:
"Module not found": Reinstall dependencies.
"Authentication failed": Regenerate app password or check 2FA.
Rate limits: OpenAI/Telegram/Google have limits; wait or upgrade plans.
Debugging: Run with python -m pdb telegram_ai_bot.py or check console logs.
No App Password Option: Use OAuth2 or SendGrid as alternatives.
Security and Best Practices
Never share .env or JSON keys.
Use strong passwords and enable 2FA.
For production: Deploy on a server (e.g., Heroku), use environment variables, and monitor logs.
Limit access: Only share Sheets with trusted users.
Compliance: Ensure email sending complies with laws (e.g., no spam).
Contributing
Fork the repo, make changes, and submit a PR.
Report issues or suggest features via GitHub.
