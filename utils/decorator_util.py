import traceback
from typing import Callable

from main import DidaManipulate


def ensure_run_retry(run: Callable):
    def wrapper(self: DidaManipulate):
        try:
            run()
        except:
            traceback.print_exc()
            self.dida.get_latest_data()
            run()
        return run()
    return wrapper
