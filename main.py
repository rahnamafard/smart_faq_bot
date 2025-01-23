import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import start, handle_question
import config

# Set the environment variable to route requests through the SOCKS5 proxy
# Check if the .env file exists
if os.path.exists(".env"):
    os.environ['http_proxy'] = "socks5://127.0.0.1:1080"
    os.environ['https_proxy'] = "socks5://127.0.0.1:1080"

def main():
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_question))

    application.run_polling()

if __name__ == "__main__":
    main()
