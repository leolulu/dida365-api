import re
from typing import List

from models.backlink import BackLink
from models.link import Link


class BackLinkUtil:
    CONTENT_TEMPLATE = "<<<<<<< Linked Reference\n{content}\n>>>>>>> End"
    SECTION_PATTERN = r"<<<<<<< Linked Reference([\s\S]*?)>>>>>>> End"
    GROUP_PATTERN = r"\* (.*)((?:\n    \* .*)+)"

    def __init__(self, task) -> None:
        self.task = task
        self.content = "" if task.content is None else task.content
        self._parse_backlink()

    def parse_normal_links(self):
        normal_section = re.sub(BackLinkUtil.SECTION_PATTERN, "", self.content)
        return Link.parse_links(normal_section)

    def _parse_backlink(self):
        backlink_section_obj = re.findall(BackLinkUtil.SECTION_PATTERN, self.content)
        self.backlinks: List[BackLink] = []
        if len(backlink_section_obj) > 0:
            self.backlink_section = backlink_section_obj[0].strip()
            groups = re.findall(BackLinkUtil.GROUP_PATTERN, self.backlink_section)
            for group in groups:
                backlink_str, refers = group
                backlink = BackLink(Link(backlink_str))
                refers = [i for i in refers.split("    * ") if (i != '\n' and i != '')]
                for refer in refers:
                    backlink.add_whole_line_str(refer.strip())
                self.backlinks.append(backlink)

                # print(f'Parse Link fail，link_str is "{link_str}", from task: {self.task.title}')

    @staticmethod
    def gen_backlink_section(backlinks: List[BackLink]):
        return BackLinkUtil.CONTENT_TEMPLATE.format(
            content="\n".join([i.gen_single_backlink_str() for i in backlinks])
        )
