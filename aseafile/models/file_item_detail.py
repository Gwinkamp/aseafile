from datetime import datetime
from .base_item import BaseItem


class FileItemDetail(BaseItem):
    size: int
    is_draft: bool
    has_draft: bool
    can_edit: bool
    draft_id: str | None
    draft_file_path: str
    starred: bool
    permission: str
    comment_total: int
    last_modified: datetime
    last_modifier_name: str
    last_modifier_email: str
    last_modifier_contact_email: str
