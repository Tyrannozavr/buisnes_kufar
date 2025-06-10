

class TelegramNotification:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    def send(self, message):
        # self.bot.send_message(self.chat_id, message)
        print("Sent telegram notification")


telegram_notification = TelegramNotification("test", "test")