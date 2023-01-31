from api.dida365 import Dida365
import re

from models.task import Task
from utils.time_util import get_days_offset, get_today_arrow

import random


class DidaManipulate:
    PROJECT_WORDS = b'\xe8\x83\x8c\xe5\x8d\x95\xe8\xaf\x8d'
    QUANTITY_LIMIT = 15 # TODO: use local only config file to control

    def __init__(self) -> None:
        self.dida = Dida365()
        self.today_arrow = get_today_arrow()

    def get_target_words_task(self):
        def condition(task: Task):
            return (
                task.repeat_flag
                and task.start_date
                and re.search(r".*FORGETTINGCURVE.*", task.repeat_flag)
                and get_days_offset(task.start_date, self.today_arrow) == 1
            )

        tasks = filter(
            lambda task:  re.search(r".*"+DidaManipulate.PROJECT_WORDS.decode('utf-8')+r"$", str(task.project_name)),
            self.dida.tasks
        )
        tasks = filter(lambda task: condition(task), tasks)
        self.tomarrow_tasks = list(tasks)

    def reallocate_task(self):
        task_len = len(self.tomarrow_tasks)
        if task_len > DidaManipulate.QUANTITY_LIMIT:
            print(f"Task quantity is {task_len}, quantity_limit is {DidaManipulate.QUANTITY_LIMIT}, will reallocate {task_len-DidaManipulate.QUANTITY_LIMIT} tasks.\n")
            tasks = random.sample(self.tomarrow_tasks, task_len-DidaManipulate.QUANTITY_LIMIT)
            for task in tasks:
                task.shift_start_date(1)
                print(f"Change start_date from [{task.org_start_date}] to [{task.shifted_start_date}], task tile is [{task.title}]")
                self.dida.update_task(Task.gen_update_date_payload(task.task_dict))
        else:
            print(f"Task quantity less than {DidaManipulate.QUANTITY_LIMIT}, skip reallocation.")


if __name__ == '__main__':
    dm = DidaManipulate()
    dm.get_target_words_task()
    dm.reallocate_task()
