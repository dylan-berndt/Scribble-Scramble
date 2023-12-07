from Crash import *


class SceneFade(Component):
    def __init__(self, group: Shader, sprite: Sprite):
        self.gameObject = None
        self.group = group
        self.sprite = sprite
        self.time = 0
        self.time_scale = 1.2

        self.is_flip = False
        self.scene = ""

        super().__init__()

        global fade
        fade = self

    def start(self):
        self.is_flip = False
        self.time = 0
        self.group["in_out"] = True
        self.group["iTime"] = 0

    def update(self, fpsDelta):
        self.time += fpsDelta

        if self.is_flip:
            self.group["iTime"] = ease_out_cubic(self.time / self.time_scale)
        else:
            self.group["iTime"] = ease_in_cubic(self.time / self.time_scale)

        if self.is_flip and self.time > self.time_scale:
            loadScene(self.scene)

    def flip(self):
        self.is_flip = True
        self.time = 0
        self.group["in_out"] = False
        self.group["iTime"] = 0


def transition_scene(scene_name):
    global fade
    if not fade.is_flip:
        fade.flip()
        fade.scene = scene_name
