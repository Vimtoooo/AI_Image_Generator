from requests.exceptions import ConnectionError, RequestException

class AssetsPathNotFoundError(Exception):
    def __init__(self, error):
        super().__init__(error)

class InvalidOperatingSystem(Exception):
    def __init__(self, error):
        super().__init__(error)

class RootProjectFolderNotFoundError(Exception):
    def __init__(self, error):
        super().__init__(error)

class ServerOfflineException(Exception):
    def __init__(self, error):
        super().__init__(error)

class WorkflowSubmissionFailedError(Exception):
    def __init__(self, error):
        super().__init__(error)