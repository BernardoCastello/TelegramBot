from app.infra.environment import TELEGRAM_TOKEN
from app.core.message_service import MessageService
from app.bot.telegram_bot import TelegramBot


def main():
    message_service = MessageService()
    bot = TelegramBot(
        token=TELEGRAM_TOKEN,
        message_service=message_service
    )
    bot.run()

if __name__ == "__main__":
    main()
