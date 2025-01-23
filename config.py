import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the TELEGRAM_TOKEN and other configurations
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
ADMIN_USER_IDS = ["371387636"]  # Replace with actual Telegram user IDs of admins

# Print the loaded token for verification
print(f"Loaded TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")

# Check if the token matches the expected format (optional)
if TELEGRAM_TOKEN is None:
    print("Error: TELEGRAM_TOKEN is not set in the .env file.")
else:
    print("TELEGRAM_TOKEN loaded successfully.")
