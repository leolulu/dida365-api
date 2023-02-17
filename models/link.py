import re


class Link:
    LINK_LINES_PATTERN = r"(.*\[.*\]\(.*\).*)"
    LINK_STR_PATTERN = r"(\[.*?\]\(.*?\))"
    LINK_PATTERN = r"\[(.*?)\]\((.*?)\)"
    URL_PATTERN = r"https://dida365.com/webapp/#p/(.*)/tasks/(.*)"
    LINK_TEMPLATE = "https://dida365.com/webapp/#p/{project_id}/tasks/{task_id}"

    def __init__(self, link_str) -> None:
        self.link_str = link_str
        self._parse_link()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Link):
            return self.link_task_id == __o.link_task_id
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.link_task_id)

    def add_whole_line_str(self, whole_line_str):
        self.whole_line_str = whole_line_str

    def _parse_link(self):
        results_obj = re.findall(Link.LINK_PATTERN, self.link_str)
        self.link_name, self.link_url = results_obj[0]
        result2_obj = re.findall(Link.URL_PATTERN, self.link_url)
        self.link_project_id, self.link_task_id = result2_obj[0]

    @staticmethod
    def parse_links(links_str):
        lines = re.findall(Link.LINK_LINES_PATTERN, links_str)
        links = []
        for whole_line_str in lines:
            whole_line_str = whole_line_str.strip()
            results = re.findall(Link.LINK_STR_PATTERN, whole_line_str)
            for result in results:
                link = Link(result)
                link.add_whole_line_str(whole_line_str)
                links.append(link)
        return links

    @staticmethod
    def dedup_link_with_wls(links):
        deduped_links = []
        _link_identifiers = set()
        for link in links:
            link_task_id = link.link_task_id
            try:
                link_whole_line_str = link.whole_line_str
            except:
                link_whole_line_str = ""
            link_identifier = link_task_id + link_whole_line_str
            if link_identifier not in _link_identifiers:
                deduped_links.append(link)
                _link_identifiers.add(link_identifier)
        return deduped_links

    @staticmethod
    def create_link_from_task(task):
        link_str = f"[{task.title}]({task.url})"
        return Link(link_str)

    def gen_link_str(self):
        return f"[{self.link_name}]({self.link_url})"
