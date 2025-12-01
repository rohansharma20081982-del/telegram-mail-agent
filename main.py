import os
import smtplib
import re
from email.mime.text import MIMEText
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables (for sensitive keys)
load_dotenv()

# API Keys and Config from .env
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMAIL_USER = os.getenv('EMAIL_USER')  # Your Gmail address (sender)
EMAIL_PASS = os.getenv('EMAIL_PASS')  # Gmail app password
SERVICE_ACCOUNT_FILE = 'telegram-bot-key.json'  # Path to your downloaded JSON key
SPREADSHEET_NAME = 'TelegramBotData'  # Name of your Google Sheet

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Google Sheets Setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME)

# Dictionary to store conversation history per user (key: user_id, value: list of messages)
conversation_histories = {}

# Function to get config from Google Sheet
def get_config(key):
    config_sheet = sheet.worksheet('Config')
    records = config_sheet.get_all_records()
    for record in records:
        if record['Key'] == key:
            return record['Value']
    return None

# Function to log to Google Sheet
def log_to_sheet(action, details):
    logs_sheet = sheet.worksheet('Logs')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs_sheet.append_row([timestamp, action, details])

# Function to send email
def send_email(subject, body, to_email, from_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        log_to_sheet('Email Sent', f'To: {to_email}, Subject: {subject}')
        return True
    except Exception as e:
        log_to_sheet('Email Error', str(e))
        return False

# Function to handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []  # Initialize empty history
    await update.message.reply_text(
        "Hello! I'm your AI chat assistant with email capabilities.\n"
        "- Chat with me for AI responses.\n"
        "- Use /email recipient@example.com Your message to send an email.\n"
        "- /clear to reset chat history.\n"
        "Data is saved to Google Sheets!"
    )

# Function to handle /email command
async def email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Parse the command: /email recipient@example.com Message
    match = re.match(r'/email\s+([^\s]+)\s+(.+)', text)
    if match:
        recipient = match.group(1)
        raw_message = match.group(2)
        
        # Validate email format (basic check)
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', recipient):
            await update.message.reply_text("Invalid email address. Use: /email recipient@example.com Your message")
            return
        
        # Use OpenAI to refine the message
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Rephrase the following message as a polite, professional email body."},
                    {"role": "user", "content": raw_message}
                ],
                max_tokens=150
            )
            polished_message = response.choices[0].message.content.strip()
        except Exception as e:
            polished_message = f"Error refining message: {e}. Original: {raw_message}"
        
        # Send email
        success = send_email("Message from Telegram AI Bot", polished_message, recipient, EMAIL_USER)
        if success:
            await update.message.reply_text(f"Email sent to {recipient} and logged to Google Sheets!")
        else:
            await update.message.reply_text("Failed to send email.")
    else:
        # Fallback: Send current conversation to default email from Sheet
        default_email = get_config('DEFAULT_EMAIL')
        if not default_email:
            await update.message.reply_text("No default email set in Google Sheet 'Config' tab.")
            return
        
        history = conversation_histories.get(user_id, [])
        if not history:
            await update.message.reply_text("No conversation to email.")
            return
        
        email_body = "Conversation History:\n\n"
        for msg in history:
            email_body += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
        
        success = send_email("AI Chat Conversation from Telegram Bot", email_body, default_email, EMAIL_USER)
        if success:
            await update.message.reply_text(f"Conversation emailed to {default_email} and logged!")
        else:
            await update.message.reply_text("Failed to send email.")

# Function to handle /clear command
async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    log_to_sheet('History Cleared', f'User: {user_id}')
    await update.message.reply_text("Conversation history cleared and logged!")

# Function to handle text messages (chat)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize history if not exists
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    
    # Add user message to history
    conversation_histories[user_id].append({"role": "user", "content": user_message})
    
    # Prepare messages for OpenAI (include system prompt and history)
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Respond naturally and engagingly in conversations."}
    ] + conversation_histories[user_id]
    
    # Get AI response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200
        )
        ai_response = response.choices[0].message.content.strip()
    except Exception as e:
        ai_response = f"Sorry, I encountered an error: {e}"
    
    # Add AI response to history
    conversation_histories[user_id].append({"role": "assistant", "content": ai_response})
    
    # Reply in Telegram
    await update.message.reply_text(ai_response)

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("email", email_command))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    application.run_polling()

if __name__ == '__main__':
    main()
