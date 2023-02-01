import json

import requests
from models.project import Project
from models.task import Task

from utils.pw_util import get_user_password


class Dida365:
    def __init__(self) -> None:
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

    def enrich_info(self):
        self._enrich_task_info()

    def _enrich_task_info(self):
        project_id_name_mapping = {p.id: p.name for p in self.projects}
        for task in self.tasks:
            task.project_name = project_id_name_mapping.get(task.project_id)

    def _get_task(self):
        tasks = self.data['syncTaskBean']['update']
        self.tasks = [Task(i) for i in tasks]

    def _get_projects(self):
        projects = self.data['projectProfiles']
        self.projects = [Project(i) for i in projects]

    def update_task(self, payload):
        url = self.base_url + "/batch/task"
        data = json.dumps(payload)
        r = self.session.request("POST", url, headers=self.headers, data=data)
        r.raise_for_status
