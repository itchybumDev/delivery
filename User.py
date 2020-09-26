from datetime import datetime

class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.is_bot = False
        self.first_name = ''
        self.last_name = ''
        self.full_name = ''
        self.username = ''
        self.joinDate = datetime.today()

    def toString(self):
        return "Fullname: {} || first_name: {} || last_name: {} || chat_id: {} || is_bot: {}".format(
            self.full_name, self.first_name, self.last_name, self.chat_id, self.is_bot)

    def toExcelRow(self):
        return "Fullname: {} || first_name: {} || last_name: {} || chat_id: {} || is_bot: {} || join: {}".format(
            self.full_name, self.first_name, self.last_name, self.chat_id, self.is_bot, self.joinDate)

    def __str__(self):
        return "{}\n".format(self.chat_id)

        # Stock {'Amzn': [5, 10]}
