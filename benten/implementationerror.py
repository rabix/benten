class ImplementationError(RuntimeError):
    def __init__(self, txt):
        super().__init__(txt + "\nPlease file an issue with full stack trace at "
                               "https://github.com/rabix/benten/issues")
