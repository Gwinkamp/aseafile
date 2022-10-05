from .base_item import BaseItem


class DirectoryItem(BaseItem):
    parent_dir: str | None
