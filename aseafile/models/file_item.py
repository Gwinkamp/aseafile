from .base_item import BaseItem


class FileItem(BaseItem):
    """Model with information about the seafile file"""
    size: int
    modifier_name: str
    modifier_email: str
    modifier_contact_email: str
    starred: bool
