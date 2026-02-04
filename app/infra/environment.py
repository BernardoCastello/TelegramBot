import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN :
    raise RuntimeError("TELEGRAM_TOKEN  não encontrada no .env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY :
    raise RuntimeError("OPENAI_API_KEY  não encontrada no .env")