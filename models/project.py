class Project:
    KIND_TASK = "TASK"

    def __init__(self, project_dict) -> None:
        self.id = project_dict.get("id")
        self.name = project_dict.get("name")
        self.group_id = project_dict.get("groupId")
        self.modified_time = project_dict.get("modifiedTime")
        self.kind = project_dict.get("kind")
