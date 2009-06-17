class ErrorWithHint(Exception):
    def __init__(self, hint, *args, **kw):
        self.hint = hint
        super(ErrorWithHint, self, *args, **kw)
