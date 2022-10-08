from .base_item import BaseItem


class DirectoryItem(BaseItem):
    """Model with information about the seafile directory"""
    parent_dir: str | None
