from datetime import datetime

class Logger:
    __instance = None

    def __init__(self, logger_window) -> None:
        self.logger_window = logger_window

        Logger.__instance = self
        pass

    @staticmethod
    def get_instance():
        return Logger.__instance

    def log_message(self, message):
        message = f"{datetime.now()}: {message}"
        self.logger_window.log_message(message)

        print(message)

