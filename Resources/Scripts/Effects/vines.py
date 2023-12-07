from Crash import *


class Vines(Component):
    def __init__(self):
        self.time = 0

        self.sprite = None

        super().__init__()

    def update(self, fpsDelta):
        if self.sprite is None:
            self.sprite = self.gameObject.getComponent(Sprite)

        self.time += fpsDelta
        self.sprite.program["iTime"] = self.time

