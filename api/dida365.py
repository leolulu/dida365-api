import copy
import json
import uuid
from io import BufferedReader

import requests
from retrying import retry

from models.project import Project
from models.task import Task
from models.upload_attachment import uploadAttachment
from utils.file_util import get_user_password
from utils.time_util import get_standard_str, get_today_arrow


class Dida365:
    def __init__(self, quick_scan_closed_task=False) -> None:
        self.quick_scan_closed_task = quick_scan_closed_task
        self.session = requests.Session()
        self.base_url = 'https://api.dida365.com/api/v2'
        self.headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-device': '{"platform":"web","os":"Windows 10","device":"Chrome 109.0.0.0","name":"","version":4411,"id":"63b0fb54363a786fba71cc80","channel":"website","campaign":"","websocket":""}',
        }
        self.login()
        self.get_latest_data()

    def login(self):
        url = self.base_url + "/user/signon?wc=true&remember=true"
        username, password = get_user_password()
        data = json.dumps({
            "username": username,
            "password": password
        })
        r = self.session.request("POST", url, headers=self.headers, data=data)
        r.raise_for_status()

    def get_latest_data(self):
        self.get_data()
        self.enrich_info()

    def get_data(self):
        url = self.base_url + "/batch/check/0"
        r = self.session.get(url, headers=self.headers)
        r.raise_for_status()
        self.data = json.loads(r.content)
        self._get_projects()
        self._get_task()

    def get_closed_task(self, project_id='all'):
        def request_data(datetime_from, datetime_to):
            url = self.base_url + f"/project/{project_id}/closed"
            params = {
                "from": get_standard_str(datetime_from),
                "to": get_standard_str(datetime_to),
                "status": "Completed"
            }
            r = self.session.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            return json.loads(r.content)

        tasks = []
        day_offset = 0
        while True:
            deadline_date = get_today_arrow().shift(weeks=-1)
            date = get_today_arrow().shift(days=-day_offset)
            datetime_from = date.replace(hour=0, minute=0, second=0)
            datetime_to = date.replace(hour=23, minute=59, second=59)
            data = request_data(datetime_from, datetime_to)
            print(f"Search completed task:[{get_standard_str(datetime_from)}]->[{get_standard_str(datetime_to)}], quantity:{len(data)}")
            if len(data) == 50:
                for hour in range(24):
                    datetime_from = datetime_from.replace(hour=hour)
                    datetime_to = datetime_to.replace(hour=hour)
                    data = request_data(datetime_from, datetime_to)
                    print(f"Search by hour:[{get_standard_str(datetime_from)}]->[{get_standard_str(datetime_to)}], ，quantity:{len(data)}")
                    tasks.extend(data)
            else:
                tasks.extend(data)
            day_offset += 1
            if self.quick_scan_closed_task:
                if date.year == deadline_date.year and date.month == deadline_date.month and date.day == deadline_date.day:
                    break
            else:
                if date.year == 2023 and date.month == 1 and date.day == 1:
                    break
        self.closed_task = [Task(i) for i in tasks]

    def enrich_info(self):
        self._enrich_task_info()

    def _enrich_task_info(self):
        project_id_name_mapping = {p.id: p.name for p in self.projects}
        for task in self.active_tasks:
            task.project_name = project_id_name_mapping.get(task.project_id)

    def _get_task(self):
        tasks = self.data['syncTaskBean']['update']
        self.active_tasks = [Task(i) for i in tasks]

    def _get_projects(self):
        projects = self.data['projectProfiles']
        self.projects = [Project(i) for i in projects]

    @retry(wait_fixed=4000, stop_max_attempt_number=5)
    def post_task(self, payload):
        url = self.base_url + "/batch/task"
        data = json.dumps(payload)
        r = self.session.request("POST", url, headers=self.headers, data=data)
        r.raise_for_status()

    @retry(wait_fixed=4000, stop_max_attempt_number=5)
    def upload_attachment(self, *attachments: uploadAttachment):
        for attachment in attachments:
            url = "https://api.dida365.com/api/v1/attachment/upload/{project_id}/{task_id}/{uuid}".format(
                project_id=attachment.project_id,
                  task_id=attachment.task_id,
                  uuid=uuid.uuid1().hex
            )
            if attachment.file_bytes is not None:
                f = attachment.file_bytes
            elif attachment.file_path is not None:
                f = open(attachment.file_path, 'rb')
            else:
                raise UserWarning(f"Attachment without neither file bytes nor file path!")
            files = [
                ('file', (attachment.file_name, f, 'application/octet-stream'))
            ]
            headers = copy.copy(self.headers)
            headers.pop('content-type')
            try:
                r = self.session.request("POST", url, headers=headers, data={}, files=files)
                r.raise_for_status()
            except:
                raise
            finally:
                if isinstance(f, BufferedReader):
                    f.close()
