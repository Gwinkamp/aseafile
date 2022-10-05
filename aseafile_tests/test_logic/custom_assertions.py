from aseafile.models import BaseItem
from typing import Callable


def contains_item(self, predicate: Callable[[BaseItem], bool]):
    items = list(filter(predicate, self.val))
    if len(items) == 0:
        return self.error(f'{items} does not contains expected item')

    return self
