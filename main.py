from app.infra.environment import TELEGRAM_TOKEN
from app.core.message_service import MessageService
from app.bot.telegram_bot import TelegramBot
from app.persistence.postgres_repository import PostgresConversationRepository



def main():
    message_service = MessageService()
    repo = PostgresConversationRepository()
    bot = TelegramBot(
        token=TELEGRAM_TOKEN,
        message_service=message_service,
        conversation_repo=repo
    )
    bot.run()

if __name__ == "__main__":
    main()
