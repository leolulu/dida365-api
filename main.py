import copy
import os
import re
from time import sleep

from api.dida365 import Dida365
from exceptions.backlink_exceptions import TaskNotFoundException
from models.backlink import BackLink
from models.link import Link
from models.target_date import TargetDate
from models.task import Task
from models.attachment import Attachment
from utils.backlink_util import BackLinkUtil
from utils.commom_util import groupby_func
from utils.decorator_util import ensure_run_retry
from utils.dict_util import BaiduFanyi
from utils.dictvoice_util import get_dictvoice_bytes
from utils.task_selector import TaskSelector
from utils.time_util import get_days_offset, get_today_arrow


class DidaManipulate:
    PROJECT_WORDS = b'\xe8\x83\x8c\xe5\x8d\x95\xe8\xaf\x8d'
    QUANTITY_LIMIT = 40  # TODO: use local only config file to control

    def __init__(self, if_get_closed_task=True, quick_scan_closed_task=False) -> None:
        self.dida = Dida365(if_get_closed_task, quick_scan_closed_task)
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
                self.dida.post_task(Task.gen_update_date_payload(task.task_dict))
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
            self.dida.post_task(Task.gen_update_date_payload(task.task_dict))

    def build_backlink(self):
        for task in [i for i in self.dida.active_tasks if i.project_id == '670946db840bf3f353ab7738']:
            normal_links = Link.dedup_link_with_wls(task._backlink_util.parse_normal_links())
            for normal_link in normal_links:
                target_tasks = [i for i in self.dida.active_tasks if i.id == normal_link.link_task_id]
                if len(target_tasks) == 0:
                    raise TaskNotFoundException()
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
                    content += "\n\n"
                    content += backlink_section_str
                else:
                    content = "" if target_task.content is None else target_task.content
                    content = re.sub(BackLinkUtil.SECTION_PATTERN, backlink_section_str, content)
                if target_task.content != content:
                    target_task.update_content(content)
                    self.dida.post_task(Task.gen_update_date_payload(target_task.task_dict))
                    print(f'{"Create" if if_add_section else "Update"} backlink: [{target_task.title}] <- [{task.title}]')

    def reset_all_backlinks(self):
        """Use with caution!!!
        """
        for task in [i for i in self.dida.active_tasks if i.project_id == '670946db840bf3f353ab7738']:
            if re.search(BackLinkUtil.SECTION_PATTERN, task.content):
                content = re.sub(BackLinkUtil.SECTION_PATTERN, "", task.content)
                task.update_content(content)
                self.dida.post_task(Task.gen_update_date_payload(task.task_dict))
                print(f"Reset backlink in task: {task.title}")

    def find_task(self, task_title, if_reload_data=False):
        if if_reload_data:
            self.dida.get_latest_data()
        tasks = [i for i in self.dida.active_tasks if i.title == task_title]
        if len(tasks) != 1:
            raise UserWarning(f"Task with title[{task_title}] duplicated, count: {len(tasks)}")
        return tasks[0]

    def _add_new_ebbinghaus_tasks(self, words):
        template_task = self.find_task('模板版本二')
        for word in words:
            new_task_dict = copy.deepcopy(template_task.task_dict)
            new_task_dict[Task.ID] = new_task_dict[Task.ID]+'z'
            title = word+"📌"
            new_task_dict[Task.TITLE] = title
            bf = BaiduFanyi(word)
            if bf.if_definitions_found:
                new_task_dict[Task.CONTENT] = bf.phonetic_string + "\n" + bf.definitions + "\n"
            print(f"Add ebbinghaus task: {title}")
            self.dida.post_task(Task.gen_add_date_payload(new_task_dict))
            # Upload attachment
            task = self.find_task(title, if_reload_data=True)
            task.add_upload_attachment_post_payload_by_bytes(*get_dictvoice_bytes(word))
            dm.dida.upload_attachment(*task.attachments_to_upload)
            print(f"Add dictvoice for task: {title}")
            # put dictvoice ahead
            self.rearrange_content_put_dictvoice_ahead(title)

        if hasattr(BaiduFanyi, 'EDGE_BROWSER'):
            BaiduFanyi.EDGE_BROWSER.close()

    def rearrange_content_put_dictvoice_ahead(self, title):
        print("Begin to rearrange content to put dictvoice ahead.")
        n = 0
        max_retry_times = 30
        while n < max_retry_times:
            task = self.find_task(title, if_reload_data=True)
            content = task.content
            if re.search(Attachment.FILE_PATTERN, content):
                file_strings = re.findall(Attachment.FILE_PATTERN, content)
                new_content = re.sub(Attachment.FILE_PATTERN, "", content).strip()
                first_line_of_content, rest_of_content = new_content.split('\n', 1)
                if re.search(r"英\[|美\[", first_line_of_content):
                    new_content = '\n'.join([
                        first_line_of_content,
                        *file_strings,
                        rest_of_content
                    ])
                else:
                    for file_string in file_strings[::-1]:
                        new_content = file_string + '\n' + new_content
                task.update_content(new_content)
                self.dida.post_task(Task.gen_update_date_payload(task.task_dict))
                break
            else:
                n += 1
                print(f"Searching for {n} times.")
                sleep(10)
        if n >= max_retry_times:
            print("Can't find attachments, content not rearranged.")
        else:
            print("Content rearranged, put dictvoice ahead.")

    def add_new_ebbinghaus_tasks_by_file(self):
        words_path = r"C:\Users\pro3\Downloads\words.txt"
        if not os.path.exists(words_path):
            print(f"No words.txt in {words_path}, skip adding new ebbinghaus tasks.")
            return
        with open(words_path, 'r', encoding='utf-8') as f:
            data = f.read().strip().split('\n')
        words = [i.strip().lower() for i in data if i.strip() != '']
        self._add_new_ebbinghaus_tasks(words)

    def add_new_ebbinghaus_tasks_by_input(self):
        word = input('Please input new word: ')
        self._add_new_ebbinghaus_tasks([word])

    @ensure_run_retry
    def run(self):
        self.perpetuate_task()
        self.build_backlink()
        self.reallocate_task(TargetDate.TOMARROW, TaskSelector.EARLY_GROUP_ROUND_ROBIN)


if __name__ == '__main__':
    dm = DidaManipulate(if_get_closed_task=False, quick_scan_closed_task=True)
    dm.add_new_ebbinghaus_tasks_by_input()
    # dm.run()
