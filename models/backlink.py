import re

from models.link import Link


class BackLink:
    LEVEL1_LIST = "* "
    LEVEL2_LIST = "    * "

    def __init__(self, link: Link) -> None:
        self.link = link
        self.whole_line_strs = set()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, BackLink):
            return self.link == __o.link
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.link)

    def add_whole_line_str(self, whole_line_str):
        self.whole_line_strs.add(whole_line_str)

    def gen_single_backlink_str(self):
        backlink_section_str = ""
        backlink_section_str += BackLink.LEVEL1_LIST
        backlink_section_str += self.link.gen_link_str()
        for whole_line_str in self.whole_line_strs:
            backlink_section_str += '\n'
            backlink_section_str += BackLink.LEVEL2_LIST
            backlink_section_str += whole_line_str
        return backlink_section_str
