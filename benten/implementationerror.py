class ImplementationError(RuntimeError):
    def __init__(self, txt):
        super().__init__(txt + " Please file an issue with full stack trace")
