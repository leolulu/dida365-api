import os
from typing import Optional


class Attachment:
    FILE_PATTERN = r"(\!\[file\]\(.*?\))"

    def __init__(self, task, file_bytes_obj: Optional[tuple] = None, file_path: Optional[str] = None) -> None:
        self.task_id = task.id
        self.project_id = task.project_id
        if file_bytes_obj:
            self.parse_file_bytes(file_bytes_obj)
        elif file_path:
            self.parse_file_path(file_path)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Attachment):
            self_file_bytes = self.file_bytes if hasattr(self, 'file_bytes') else ""
            self_file_path = self.file_path if hasattr(self, 'file_path') else ""
            __o_file_bytes = __o.file_bytes if hasattr(__o, 'file_bytes') else ""
            __o_file_path = __o.file_path if hasattr(__o, 'file_path') else ""
            return str(self_file_bytes) + str(self_file_path) == str(__o_file_bytes) + str(__o_file_path)
        else:
            return False

    def __hash__(self) -> int:
        self_file_bytes = self.file_bytes if hasattr(self, 'file_bytes') else ""
        self_file_path = self.file_path if hasattr(self, 'file_path') else ""
        return hash(str(self_file_bytes)+str(self_file_path))

    def parse_file_bytes(self, file_bytes_obj):
        file_name, self.file_bytes = file_bytes_obj
        self.file_name = file_name.lower()+'.mp3'

    def parse_file_path(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
