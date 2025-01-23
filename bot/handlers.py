import logging
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from bot.knowledge_base import add_knowledge, remove_knowledge, get_knowledge_base, query_gemini_llm, get_answer
import config
from bot.database import remove_all_knowledge  # Ensure this is correct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Bot started by user: %s", update.message.from_user.id)
    await update.message.reply_text("Hello! Ask me anything, and I'll try to help based on my knowledge base.")

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    logger.info("Received question from user: %s", user_id)
    
    if str(user_id) in config.ADMIN_USER_IDS:
        logger.info("User %s is an admin.", user_id)
        await handle_admin_commands(update, context)
    else:
        logger.info("User %s is a regular user.", user_id)
        await handle_user_question(update, context)

async def handle_user_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text
    logger.info("User asked: %s", question)
    
    # Get the answer from the knowledge base
    answer = get_answer(question)
    
    if answer:
        try:
            # Use the Gemini API for humanizing the answer
            humanized_answer = query_gemini_llm(answer)  # Attempt to humanize the answer
            await update.message.reply_text(humanized_answer)
        except Exception as e:
            logger.error("Error during humanization: %s", e)
            # If an error occurs, return the original answer
            await update.message.reply_text(answer)
    else:
        # If not found, query the Gemini API for help
        answer = query_gemini_llm(question)  # Use Gemini API for the answer
        await update.message.reply_text("I couldn't find an exact match. Please ask me another queestion.")

async def handle_admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text
    logger.info("Admin command received: %s", command)
    
    if command.startswith("/"):
        logger.info("Processing command: %s", command)
        if command == "/view_kb":
            logger.info("Fetching knowledge base for admin: %s", update.message.from_user.id)
            knowledge_base = get_knowledge_base()
            # Format the knowledge base entries into strings
            formatted_kb = [f"Q: {q}\nA: {a}" for q, a in knowledge_base]  # Create a list of formatted strings
            await update.message.reply_text("\n\n".join(formatted_kb))  # Join with double newlines for better readability
        elif command.startswith("/add_kb"):
            # Expecting the format: /add_kb question - answer
            try:
                new_entry = command[len("/add_kb "):]  # Get the new entry from the command
                question, answer = new_entry.split(" - ")
                add_knowledge(question.strip(), answer.strip())  # Insert question and answer
                logger.info("New entry added to the knowledge base: %s - %s", question, answer)
                await update.message.reply_text("New entry added to the knowledge base.")
            except ValueError:
                logger.warning("Invalid format for adding knowledge: %s", command)
                await update.message.reply_text("Please use the format: /add_kb question - answer")
        elif command.startswith("/remove_kb"):
            entry_to_remove = command[len("/remove_kb "):]  # Get the entry to remove
            if remove_knowledge(entry_to_remove):
                logger.info("Entry removed from the knowledge base: %s", entry_to_remove)
                await update.message.reply_text("Entry removed from the knowledge base.")
            else:
                logger.warning("Entry not found for removal: %s", entry_to_remove)
                await update.message.reply_text("Entry not found.")
        elif command == "/reset_kb":  # New command to reset the knowledge base
            logger.info("Resetting knowledge base for admin: %s", update.message.from_user.id)
            remove_all_knowledge()  # Call the function to clear the knowledge base
            await update.message.reply_text("Knowledge base has been reset and cleared.")
    else:
        logger.warning("Received non-command input from admin: %s", command)
