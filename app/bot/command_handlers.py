from telegram import Update
from telegram.ext import ContextTypes

class CommandHandlers:

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Olá! 🤖\n"
            "Sou um bot-portfólio do Bernardo Castello.\n"
            "Pergunte sobre minha formação, experiência, tecnologias ou projetos.\n\n"
            "Use /help para ver os comandos de links uteis ou pergunte normalmente."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "/start - Iniciar conversa\n"
            "/help - Mostrar ajuda\n"
            "/github - Link do GitHub\n"
            "/linkedin - Link do LinkedIn\n"
            "/email - Email para contato"
        )

    async def github(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "GitHub: https://github.com/BernardoCastello"
        )

    async def linkedin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "LinkedIn: https://www.linkedin.com/in/bernardo-castello-silva/"
        )

    async def email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Email: becastellosilva@gmail.com"
        )
