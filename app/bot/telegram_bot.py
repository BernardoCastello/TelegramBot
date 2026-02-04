from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler
)
from app.core.message_service import MessageService
from app.bot.command_handlers import CommandHandlers


class TelegramBot:
    def __init__(self, token: str, message_service: MessageService):
        self.token = token
        self.message_service = message_service
        self.commands = CommandHandlers()

        self.app = ApplicationBuilder().token(self.token).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.commands.start))
        self.app.add_handler(CommandHandler("help", self.commands.help))
        self.app.add_handler(CommandHandler("github", self.commands.github))
        self.app.add_handler(CommandHandler("linkedin", self.commands.linkedin))
        self.app.add_handler(CommandHandler('email', self.commands.email))

        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.responder)
        )

    async def responder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        texto = update.message.text

        resposta = self.message_service.process_message(texto)

        await update.message.reply_text(resposta)

    def run(self):
        print("Bot rodando...")
        self.app.run_polling()

