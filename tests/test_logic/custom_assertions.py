from typing import Callable, Any


def contains_item(self, predicate: Callable[[Any], bool]):
    items = list(filter(predicate, self.val))
    if len(items) == 0:
        return self.error(f'{items} does not contains expected item')

    return self
