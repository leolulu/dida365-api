class Task:
    KIND_CHECKLIST = "CHECKLIST"
    KIND_TEXT = "TEXT"
    ID = "id"
    PROJECT_ID = "projectId"
    TITLE = "title"
    CONTENT = "content"
    START_DATE = "startDate"
    MODIFIED_TIME = "modifiedTime"
    DUE_DATE = "dueDate"
    REPEAT_FLAG = "repeatFlag"
    REPEAT_FIRST_DATE = "repeatFirstDate"
    KIND = "kind"

    def __init__(self, task_dict) -> None:
        self.task_dict = task_dict
        self.id = task_dict.get(Task.ID)
        self.project_id = task_dict.get(Task.PROJECT_ID)
        self.project_name = None
        self.title = task_dict.get(Task.TITLE)
        self.content = task_dict.get(Task.CONTENT)
        self.start_date = task_dict.get(Task.START_DATE)
        self.modified_time = task_dict.get(Task.MODIFIED_TIME)
        self.due_date = task_dict.get(Task.DUE_DATE)
        self.repeat_flag = task_dict.get(Task.REPEAT_FLAG)
        self.repeat_first_date = task_dict.get(Task.REPEAT_FIRST_DATE)
        self.kind = task_dict.get(Task.KIND)
