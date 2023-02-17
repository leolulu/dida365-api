import random
import re

from api.dida365 import Dida365
from models.backlink import BackLink
from models.link import Link
from models.target_date import TargetDate
from models.task import Task
from utils.backlink_util import BackLinkUtil
from utils.commom_util import groupby_func
from utils.task_selector import TaskSelector
from utils.time_util import get_days_offset, get_today_arrow


class DidaManipulate:
    PROJECT_WORDS = b'\xe8\x83\x8c\xe5\x8d\x95\xe8\xaf\x8d'
    QUANTITY_LIMIT = 20  # TODO: use local only config file to control

    def __init__(self) -> None:
        self.dida = Dida365()
        self.today_arrow = get_today_arrow()

    def _get_target_words_task(self, start_day_offset):
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

    def reallocate_task(self, start_day_offset, selector):
        self._get_target_words_task(start_day_offset)
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

    def build_backlink(self):
        for task in [i for i in self.dida.active_tasks if i.project_id == '670946db840bf3f353ab7738']:
            # if not re.match("双链测试任务", task.title):
            #     continue
            normal_links = Link.dedup_link_with_wls(task._backlink_util.parse_normal_links())
            for normal_link in normal_links:
                target_tasks = [i for i in self.dida.active_tasks if i.id == normal_link.link_task_id]
                target_task = target_tasks[0]
                if len(target_tasks) > 1:
                    raise UserWarning(f"Task id duplicates, id: {normal_link.link_task_id}")
                target_task_backlinks = target_task.backlinks
                if len(target_task_backlinks) == 0:
                    if_add_section = True
                else:
                    if_add_section = False
                task_link = Link.create_link_from_task(task)
                backlink = BackLink(task_link)
                if backlink not in target_task_backlinks:
                    backlink.add_whole_line_str(normal_link.whole_line_str)
                    target_task_backlinks.append(backlink)
                else:
                    backlink = target_task_backlinks[target_task_backlinks.index(backlink)]
                    backlink.add_whole_line_str(normal_link.whole_line_str)
                backlink_section_str = BackLinkUtil.gen_backlink_section(target_task_backlinks)
                if if_add_section:
                    content = "" if target_task.content is None else target_task.content
                    content += "\n\n\n"
                    content += backlink_section_str
                else:
                    content = "" if target_task.content is None else target_task.content
                    content = re.sub(BackLinkUtil.SECTION_PATTERN, backlink_section_str, content)
                if target_task.content != content:
                    target_task.update_content(content)
                    self.dida.update_task(Task.gen_update_date_payload(target_task.task_dict))
                    print(f'{"Create" if if_add_section else "Update"} backlink: [{target_task.title}] <- [{task.title}]')

    def reset_all_backlinks(self):
        """Use with caution!!!
        """
        for task in [i for i in self.dida.active_tasks if i.project_id == '670946db840bf3f353ab7738']:
            if re.search(BackLinkUtil.SECTION_PATTERN, task.content):
                content = re.sub(BackLinkUtil.SECTION_PATTERN, "", task.content)
                task.update_content(content)
                self.dida.update_task(Task.gen_update_date_payload(task.task_dict))
                print(f"Reset backlink in task: {task.title}")


if __name__ == '__main__':
    dm = DidaManipulate()
    dm.perpetuate_task()
    dm.build_backlink()
    # dm.reallocate_task(TargetDate.TOMARROW, TaskSelector.EARLIEST_START_DATE)
