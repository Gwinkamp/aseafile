from __future__ import annotations
from typing import Type, TypeVar, Any
import json
import codecs

T = TypeVar('T')


class TestContext:

    def __init__(self):
        self._context_data = dict()

    def add(self, key: str, value: Any) -> None:
        self._context_data[key] = value

    def get(self, key: str) -> Any:
        return self._context_data.get(key)

    def typed_get(self, key: str, content_type: Type[T]) -> T:
        return self._context_data.get(key)

    @staticmethod
    def from_dict(data: dict) -> TestContext:
        context = TestContext()

        for key, value in data.items():
            context.add(key, value)

        return context

    @staticmethod
    def from_json_file(path_to_file: str) -> TestContext:
        with codecs.open(path_to_file, 'r', encoding='utf-8') as json_file:
            json_content: dict = json.load(json_file)

        return TestContext.from_dict(json_content)
