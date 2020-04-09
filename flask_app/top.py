import time
from typing import List, Dict

REFRESH_DELAY = 100


class Top:
    def __init__(self):
        self.last_update = 0

    def refresh(self):
        self.last_update = time.time()

    def get_first(self, count: int) -> List[Dict]:
        if time.time() - self.last_update > REFRESH_DELAY:
            self.refresh()

