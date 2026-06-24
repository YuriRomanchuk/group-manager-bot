import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",")]
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE", "Welcome to the group, {user}!")
ANTI_SPAM = os.getenv("ANTI_SPAM", "true").lower() == "true"
MAX_WARNINGS = int(os.getenv("MAX_WARNINGS", "3"))
LOG_CHANNEL = os.getenv("LOG_CHANNEL", "")
