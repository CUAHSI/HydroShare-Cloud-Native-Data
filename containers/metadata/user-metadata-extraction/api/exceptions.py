class RepositoryException(Exception):
    def __init__(self, status_code: int, detail: str):
        self._status_code = status_code
        self._detail = detail

    @property
    def detail(self):
        return self._detail

    @property
    def status_code(self):
        return self._status_code
