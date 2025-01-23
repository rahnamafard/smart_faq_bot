import os
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from bot.handlers import start, handle_question
import config
from dotenv import load_dotenv

# Remove the old TELEGRAM_TOKEN if it exists
os.environ.pop("TELEGRAM_TOKEN", None)

# Load environment variables from .env file
load_dotenv()

# Fetch the TELEGRAM_TOKEN and other configurations
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Set the environment variable to route requests through the SOCKS5 proxy
# Check if the .env file exists
if os.path.exists(".env"):
    os.environ['http_proxy'] = "socks5://127.0.0.1:1080"
    os.environ['https_proxy'] = "socks5://127.0.0.1:1080"

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("shuffle_database", handle_question))  # Ensure command is handled
    application.add_handler(MessageHandler(filters.TEXT, handle_question))  # Handle regular questions

    application.run_polling()

if __name__ == "__main__":
    main()
