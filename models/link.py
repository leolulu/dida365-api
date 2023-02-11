import re


class Link:
    LINKS_PATTERN = r"(.*(\[.*\]\(.*\)).*)"
    LINK_PATTERN = r"\[(.*)\]\((.*)\)"
    URL_PATTERN = r"https://dida365.com/webapp/#p/(.*)/tasks/(.*)"
    LINK_TEMPLATE = "https://dida365.com/webapp/#p/{project_id}/tasks/{task_id}"

    def __init__(self, link_str) -> None:
        self.link_str = link_str
        self.parse_link()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Link):
            return self.link_task_id == __o.link_task_id
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.link_task_id)

    def add_whole_line_str(self, whole_line_str):
        self.whole_line_str = whole_line_str

    def parse_link(self):
        results_obj = re.findall(Link.LINK_PATTERN, self.link_str)
        self.link_name, self.link_url = results_obj[0]
        result2_obj = re.findall(Link.URL_PATTERN, self.link_url)
        self.link_project_id, self.link_task_id = result2_obj[0]

    @staticmethod
    def parse_links(links_str):
        results = re.findall(Link.LINKS_PATTERN, links_str)
        links = []
        for result in results:
            whole_line_str = result[0]
            link_str = result[1]
            link = Link(link_str)
            link.add_whole_line_str(whole_line_str)
            links.append(link)
        return links

    @staticmethod
    def create_link(task):
        link_str = f"[{task.title}]({task.url})"
        return Link(link_str)
