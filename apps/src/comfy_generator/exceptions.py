from requests.exceptions import ConnectionError, RequestException

class AssetsPathNotFoundError(Exception):
    def __init__(self, error):
        super().__init__(error)

class InvalidFileTypeError(Exception):
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

class WorkflowNotDefinedError(Exception):
    def __init__(self, error):
        super().__init__(error)

class WorkflowSubmissionFailedError(Exception):
    def __init__(self, error):
        super().__init__(error)


class SceneExecutionError(WorkflowSubmissionFailedError):
    """A scene failed locally; server work may still exist after submission."""

    def __init__(self, message, *, stage, prompt_id=None, submission_unknown=False):
        super().__init__(message)
        self.stage = stage
        self.prompt_id = prompt_id
        self.submission_unknown = submission_unknown


class SceneStopped(Exception):
    """Stop won the submission boundary; no prompt was sent."""
