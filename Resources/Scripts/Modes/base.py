

class GameClient:
    def __init__(self):
        pass


class GameHost:
    def __init__(self):
        pass


class Game:
    def __init__(self):
        self.client = self.Client()
        self.host = self.Host()

    class Client(GameClient):
        def __init__(self):
            super().__init__()
            raise NotImplementedError

    class Host(GameHost):
        def __init__(self):
            super().__init__()
            raise NotImplementedError

