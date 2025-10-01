class Progress:
    def __init__(self):
        pass

    def update_progress(self, progress: int):
        pass

    def info(self, text: str):
        pass

    def error(self, text: str):
        pass

    def warning(self, text: str):
        pass

    def update_info(self, progress: int, text: str):
        pass

    def update_error(self, progress: int, text: str):
        pass

    def update_warning(self, progress: int, text: str):
        pass

    def reset_progress(self):
        pass

    def set_progress_unknown(self):
        pass
