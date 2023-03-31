class Session:
    def __init__(self, enter=None, exit=None):
        self.enter = enter
        self.exit = exit

    def __enter__(self, *args, **kwargs):
        if self.enter is not None:
            self.enter(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        if self.exit is not None:
            self.exit(*args, **kwargs)
