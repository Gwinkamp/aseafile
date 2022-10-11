from typing import Dict


class QueryParams:
    """Query parameters builder"""

    def __init__(self):
        self._query_params: Dict[str, str | int] = dict()

    def reset(self):
        self._query_params = dict()

    def get_result(self):
        if not self._query_params:
            return None

        result = self._query_params
        self.reset()
        return result

    def add_param(self, key: str, value: str | int):
        self._query_params[key] = value

    def add_param_if_exists(self, key: str, value: str | int | None):
        if value is not None:
            self.add_param(key, value)
