import re
from models.link import Link


class BackLink:
    CONTENT_TEMPLATE = "<<<<<<< Linked Reference\n{content}\n>>>>>>> End"
    PATTERN = r"<<<<<<< Linked Reference([\s\S]*?)>>>>>>> End"

    def __init__(self, task) -> None:
        self.task = task
        self.content = task.content
        self._parse_backlink()

    def parse_normal_links(self):
        normal_section = re.sub(BackLink.PATTERN, "", self.content)
        return Link.parse_links(normal_section)

    def _parse_backlink(self):
        result_obj = re.findall(BackLink.PATTERN, self.content)
        self.links = []
        if len(result_obj) > 0:
            self.backlink_section = result_obj[0].strip()
            self.links_str = self.backlink_section.split('\n')
            for link_str in self.links_str:
                try:
                    link = Link(link_str)
                    self.links.append(link)
                except Exception as e:
                    print(f'Parse Link fail，link_str is "{link_str}", from task: {self.task.title}')

    @staticmethod
    def gen_backlink_section(links):
        return BackLink.CONTENT_TEMPLATE.format(
            content = "\n".join([i.link_str for i in links])
        )
