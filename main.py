import random
import re

from api.dida365 import Dida365
from models.target_date import TargetDate
from models.task import Task
from utils.commom_util import groupby_func
from utils.task_selector import TaskSelector
from utils.time_util import get_days_offset, get_today_arrow


class DidaManipulate:
    PROJECT_WORDS = b'\xe8\x83\x8c\xe5\x8d\x95\xe8\xaf\x8d'
    QUANTITY_LIMIT = 20  # TODO: use local only config file to control

    def __init__(self) -> None:
        self.dida = Dida365()
        self.today_arrow = get_today_arrow()

    def get_target_words_task(self, start_day_offset):
        def condition(task: Task):
            return (
                task.repeat_flag
                and task.start_date
                and re.search(r".*FORGETTINGCURVE.*", task.repeat_flag)
                and get_days_offset(task.start_date, self.today_arrow) == start_day_offset
            )

        tasks = filter(
            lambda task:  re.search(r".*"+DidaManipulate.PROJECT_WORDS.decode('utf-8')+r"$", str(task.project_name)),
            self.dida.active_tasks
        )
        tasks = filter(lambda task: condition(task), tasks)
        self.target_tasks = list(tasks)

    def reallocate_task(self, selector):
        task_len = len(self.target_tasks)
        reallocation_len = task_len-DidaManipulate.QUANTITY_LIMIT
        if task_len > DidaManipulate.QUANTITY_LIMIT:
            print(f"Task quantity is {task_len}, quantity_limit is {DidaManipulate.QUANTITY_LIMIT}, will reallocate {reallocation_len} tasks.\n")
            task_selector = TaskSelector(self.target_tasks, reallocation_len)
            for task in task_selector.select_task(selector):
                task.shift_start_date(1)
                print(f"Change start_date from [{task.org_start_date}] to [{task.shifted_start_date}], task created_time is [{task.created_time}], title is [{task.title}]")
                self.dida.update_task(Task.gen_update_date_payload(task.task_dict))
        else:
            print(f"Task quantity less than {DidaManipulate.QUANTITY_LIMIT}, skip reallocation.")

    def perpetuate_task(self):
        tasks = self.dida.closed_task
        tasks_dictincted = []
        for key, value in groupby_func(tasks, lambda x: x.title).items():
            value = sorted(value, key=lambda x: x.completed_time, reverse=True)
            tasks_dictincted.append(value[0])
        tasks_to_perpetuate = []
        for task in tasks_dictincted:
            active_task_titles = [i.title for i in self.dida.active_tasks]
            if task.title not in active_task_titles:
                tasks_to_perpetuate.append(task)
        for task in tasks_to_perpetuate:
            task.perpetuate_task()
            print(f"Perpetuate task: {task.title}")
            self.dida.update_task(Task.gen_update_date_payload(task.task_dict))


if __name__ == '__main__':
    dm = DidaManipulate()
    # dm.get_target_words_task(TargetDate.TODAY)
    # dm.reallocate_task(TaskSelector.EARLY_GROUP_ROUND_ROBIN)

    dm.perpetuate_task()
