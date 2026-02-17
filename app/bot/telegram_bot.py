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

import asyncio

class TelegramBot:
    def __init__(self, token: str, message_service: MessageService, conversation_repo=None):
        self.token = token
        self.message_service = message_service
        self.conversation_repo = conversation_repo
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
        chat_id = update.effective_chat.id
        texto = update.message.text

        # salvar mensagem do usuário (síncrono)
        try:
            if self.conversation_repo:
                self.conversation_repo.add_message(chat_id, "user", texto)
        except Exception:
            pass

        resposta = self.message_service.process_message(texto, chat_id=chat_id, conversation_repo=self.conversation_repo)

        # salvar resposta do bot (síncrono) — apenas UMA vez
        try:
            if self.conversation_repo:
                self.conversation_repo.add_message(chat_id, "assistant", resposta)
        except Exception:
            pass

        await update.message.reply_text(resposta)

    def run(self):
        print("Bot rodando...")
        self.app.run_polling()