from api.dida365 import Dida365
import re


class DidaManipulate:
    PROJECT_WORDS = b'\xe8\x83\x8c\xe5\x8d\x95\xe8\xaf\x8d'

    def __init__(self) -> None:
        self.dida = Dida365()

    def get_words_task(self):
        for task in self.dida.tasks:
            if re.search(r".*"+DidaManipulate.PROJECT_WORDS.decode('utf-8')+r"$", str(task.project_name)):
                print(task.project_name,task.title)


if __name__ == '__main__':
    dm = DidaManipulate()
    dm.get_words_task()
