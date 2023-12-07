from .base import *


class Classic(Game):
    def __init__(self):
        super().__init__()

    class Client(GameClient):
        def __init__(self):
            super().__init__()

    class Host(GameHost):
        def __init__(self):
            super().__init__()
