import traceback
from typing import Callable


def ensure_run_retry(run: Callable):
    def wrapper(self, *args):
        try:
            run(self, *args)
        except:
            traceback.print_exc()
            self.dida.get_latest_data()
            run(self, *args)
    return wrapper
