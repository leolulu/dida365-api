import random
from itertools import groupby
from typing import List

from models.task import Task
from utils.time_util import get_days_offset, get_today_arrow


class TaskSelector:
    RANDOM_SAMPLE = 'selector_random_sample'
    EARLIEST_START_DATE = 'selector_earliest_start_date'
    EARLY_GROUP_ROUND_ROBIN = 'selector_early_group_round_robin'

    def __init__(self, target_tasks: List[Task], reallocation_len=0) -> None:
        self.target_tasks = target_tasks
        self.reallocation_len = reallocation_len

    def _random_sample(self):
        return random.sample(self.target_tasks, self.reallocation_len)

    def _earliest_start_date(self):
        return sorted(self.target_tasks, key=lambda x: x.created_time)[:self.reallocation_len]

    def _early_group_round_robin(self):
        tasks = sorted(self.target_tasks, key=lambda x: x.created_time)
        create_time_task_mapping = [[i[0], list(i[1])] for i in groupby(tasks, lambda x:x.created_time.replace(hour=0, minute=0, second=0))]
        task_group = [i for i in create_time_task_mapping if get_days_offset(get_today_arrow(), i[0]) > 3]
        task_group = [i[1] for i in task_group]
        tasks_to_reallocate = []
        n = self.reallocation_len
        i = 0
        while n > 0:
            l = task_group[i % len(task_group)]
            if set([len(i) for i in task_group]) == set([0]):
                break
            if len(l) == 0:
                i += 1
                continue
            task = l.pop(random.randint(0, len(l)-1))
            tasks_to_reallocate.append(task)
            n -= 1
            i += 1
        return tasks_to_reallocate

    def select_task(self, selector, **kwargs):
        if selector == TaskSelector.RANDOM_SAMPLE:
            tasks = self._random_sample()
        elif selector == TaskSelector.EARLIEST_START_DATE:
            tasks = self._earliest_start_date()
        elif selector == TaskSelector.EARLY_GROUP_ROUND_ROBIN:
            tasks = self._early_group_round_robin()
        else:
            raise UserWarning(f"Selector[{selector}] not exists.")
        return tasks
