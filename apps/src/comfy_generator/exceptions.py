class InvalidOperatingSystem(Exception):
    def __init__(self, error):
        super().__init__(error)

class NonSettableInstanceException(Exception):
    def __init__(self, error):
        super().__init__(error)

class AssetsPathNotFoundError(Exception):
    def __init__(self, error):
        super().__init__(error)