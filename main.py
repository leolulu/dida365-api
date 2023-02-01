import random
import re

from api.dida365 import Dida365
from models.selector import Selector
from models.target_date import TargetDate
from models.task import Task
from utils.time_util import get_days_offset, get_today_arrow


class DidaManipulate:
    PROJECT_WORDS = b'\xe8\x83\x8c\xe5\x8d\x95\xe8\xaf\x8d'
    QUANTITY_LIMIT = 15 # TODO: use local only config file to control

    def __init__(self) -> None:
        self.dida = Dida365()
        self.today_arrow = get_today_arrow()

    def get_target_words_task(self, day_offset):
        def condition(task: Task):
            return (
                task.repeat_flag
                and task.start_date
                and re.search(r".*FORGETTINGCURVE.*", task.repeat_flag)
                and get_days_offset(task.start_date, self.today_arrow) == day_offset
            )

        tasks = filter(
            lambda task:  re.search(r".*"+DidaManipulate.PROJECT_WORDS.decode('utf-8')+r"$", str(task.project_name)),
            self.dida.tasks
        )
        tasks = filter(lambda task: condition(task), tasks)
        self.target_tasks = list(tasks)

    def reallocate_task(self, selector):
        task_len = len(self.target_tasks)
        reallocation_len = task_len-DidaManipulate.QUANTITY_LIMIT
        if task_len > DidaManipulate.QUANTITY_LIMIT:
            print(f"Task quantity is {task_len}, quantity_limit is {DidaManipulate.QUANTITY_LIMIT}, will reallocate {reallocation_len} tasks.\n")
            if selector == Selector.RANDOM_SAMPLE:
                tasks = random.sample(self.target_tasks, reallocation_len)
            elif selector == Selector.EARLIEST_START_DATE:
                tasks = sorted(self.target_tasks, key=lambda x: x.created_time)[:reallocation_len]

            else:
                raise UserWarning(f"Selector[{selector}] not exists.")
            for task in tasks:
                task.shift_start_date(1)
                print(f"Change start_date from [{task.org_start_date}] to [{task.shifted_start_date}], task created_time is [{task.created_time}], title is [{task.title}]")
                self.dida.update_task(Task.gen_update_date_payload(task.task_dict))
        else:
            print(f"Task quantity less than {DidaManipulate.QUANTITY_LIMIT}, skip reallocation.")


if __name__ == '__main__':
    dm = DidaManipulate()
    dm.get_target_words_task(TargetDate.TOMARROW)
    dm.reallocate_task(Selector.EARLIEST_START_DATE)
