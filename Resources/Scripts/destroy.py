from Crash import *


class Destroy(Component):
    def __init__(self, lifetime):
        self.gameObject = None
        self.lifetime = lifetime

    def update(self, fpsDelta):
        self.lifetime -= fpsDelta
        if self.lifetime <= 0:
            destroy(self.gameObject)
