from app.infra.environment import TELEGRAM_TOKEN
from app.core.message_service import MessageService
from app.bot.telegram_bot import TelegramBot
from app.persistence.postgres_repository import PostgresConversationRepository
from app.persistence.mongo_repository import MongoConversationRepository



def main():
    message_service = MessageService()
    # repositório de resumo / contadores (Postgres)
    postgres_repo = PostgresConversationRepository()
    # repositório de mensagens (MongoDB)
    mongo_repo = MongoConversationRepository()

    bot = TelegramBot(
        token=TELEGRAM_TOKEN,
        message_service=message_service,
        message_repo=mongo_repo,
        conversation_repo=postgres_repo
    )
    bot.run()

if __name__ == "__main__":
    main()
