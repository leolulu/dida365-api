from models.attachment import Attachment
from models.upload_attachment import uploadAttachment
from models.link import Link
from utils.backlink_util import BackLinkUtil
from utils.time_util import get_prc_arrow, get_utc_str


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
    CREATED_TIME = "createdTime"
    KIND = "kind"
    COMPLETED_TIME = "completedTime"
    STATUS = "status"
    ATTACHMENTS = "attachments"
    STATUS_ACTIVE = 0
    STATUS_COMPLETED = 2

    def __init__(self, task_dict) -> None:
        self.task_dict = task_dict
        self._load_field()
        self._datetime_format()

    def _load_field(self):
        self.id = self.task_dict.get(Task.ID)
        self.project_id = self.task_dict.get(Task.PROJECT_ID)
        self.url = Link.LINK_TEMPLATE.format(project_id=self.project_id, task_id=self.id)
        self.project_name = None
        self.title = self.task_dict.get(Task.TITLE)
        self._load_field_content()
        self.start_date = self.task_dict.get(Task.START_DATE)
        self.modified_time = self.task_dict.get(Task.MODIFIED_TIME)
        self.created_time = self.task_dict.get(Task.CREATED_TIME)
        self.due_date = self.task_dict.get(Task.DUE_DATE)
        self.repeat_flag = self.task_dict.get(Task.REPEAT_FLAG)
        self.repeat_first_date = self.task_dict.get(Task.REPEAT_FIRST_DATE)
        self.kind = self.task_dict.get(Task.KIND)
        self.completed_time = self.task_dict.get(Task.COMPLETED_TIME)
        self.status = self.task_dict.get(Task.STATUS)
        self._backlink_util = BackLinkUtil(self)
        self.backlinks = self._backlink_util.backlinks
        self._load_field_attachments()
        self.attachments_to_upload = set()

    def _load_field_attachments(self):
        attachments = self.task_dict.get(Task.ATTACHMENTS)
        if attachments and isinstance(attachments, list):
            attachments = [Attachment(i) for i in attachments]
            self.attachments = [i for i in attachments if i.is_active]
        else:
            self.attachments = []

    def _load_field_content(self):
        content = self.task_dict.get(Task.CONTENT)
        if content:
            content = content.replace('\r\n', '\n')
            self.task_dict[Task.CONTENT] = content
        self.content = content

    def _datetime_format(self):
        if self.start_date:
            self.start_date = get_prc_arrow(self.start_date)
        if self.due_date:
            self.due_date = get_prc_arrow(self.due_date)
        if self.repeat_first_date:
            self.repeat_first_date = get_prc_arrow(self.repeat_first_date)
        if self.modified_time:
            self.modified_time = get_prc_arrow(self.modified_time)
        if self.created_time:
            self.created_time = get_prc_arrow(self.created_time)
        if self.completed_time:
            self.completed_time = get_prc_arrow(self.completed_time)

    @staticmethod
    def _gen_post_task_payload():
        payload = dict()
        payload['add'] = []
        payload['addAttachments'] = []
        payload['delete'] = []
        payload['deleteAttachments'] = []
        payload['update'] = []
        payload['updateAttachments'] = []
        return payload

    @staticmethod
    def gen_update_date_payload(new_task_dict):
        payload = Task._gen_post_task_payload()
        payload['update'] = [new_task_dict]
        return payload

    @staticmethod
    def gen_add_date_payload(new_task_dict):
        payload = Task._gen_post_task_payload()
        payload['add'] = [new_task_dict]
        return payload

    def shift_start_date(self, days):
        self.org_start_date = self.start_date
        start_date = self.start_date.shift(days=days)
        self.shifted_start_date = start_date
        self.start_date = get_utc_str(start_date)
        self.task_dict[Task.START_DATE] = self.start_date

    def change_status(self, status):
        self.status = status
        self.task_dict[Task.STATUS] = self.status

    def perpetuate_task(self):
        self.change_status(Task.STATUS_ACTIVE)
        self.start_date = get_utc_str(self.start_date.replace(year=2099, month=12, day=31))
        self.task_dict[Task.START_DATE] = self.start_date

    def update_content(self, content):
        self.content = content
        self.task_dict[Task.CONTENT] = self.content

    def add_upload_attachment_post_payload_by_path(self, file_path):
        self.attachments_to_upload.add(
            uploadAttachment(self, file_path == file_path)
        )

    def add_upload_attachment_post_payload_by_bytes(self, *file_bytes_objs):
        for file_bytes_obj in file_bytes_objs:
            self.attachments_to_upload.add(
                uploadAttachment(self, file_bytes_obj=file_bytes_obj)
            )
