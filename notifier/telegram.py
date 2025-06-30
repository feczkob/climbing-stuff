from telegram import Bot

def send_telegram_message(body):
    bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
    chat_id = 'YOUR_CHAT_ID'  # Hardcoded chat ID
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=body) 