import traceback
from typing import Callable


def ensure_run_retry(run: Callable):
    def wrapper(self):
        try:
            run(self)
        except:
            traceback.print_exc()
            self.dida.get_latest_data()
            run(self)
        return run()
    return wrapper
