from .base_item import BaseItem


class RepoItem(BaseItem):
    """Model with information about the seafile repository"""
    size: int
    owner: str
