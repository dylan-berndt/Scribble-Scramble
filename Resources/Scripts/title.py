from Crash import *
from Resources.Scripts.destroy import Destroy


class Title(Component):
    def __init__(self):
        self.gameObject = None

        self.bubbles = []
        renderer = Sprite("Sprites/Title/Bubble/bubble01.png", batch="default", group=2)
        self.bubble = GameObject(Vector2(0, 0), "bubble", active=False).\
            addComponent(renderer).\
            addComponent(Animator({"idle": animation_from_folder("Sprites/Title/Bubble/", renderer, 24)}, "idle")).\
            addComponent(Rigidbody(velocity=Vector2(0, 6.5)))
        self.bubble.getComponent(Sprite).visible = False
        self.bubble_time = 4
        self.bubble_time_left = 0
        self.bubble_interval = 0.1

    def update(self, fpsDelta):
        if self.bubble_time_left > 0:
            before = self.bubble_time_left % self.bubble_interval
            after = before - fpsDelta
            should = (self.bubble_time_left - fpsDelta) % self.bubble_interval
            if after != should:
                new = instantiate(self.bubble, "buble" + str(self.bubble_time_left), active=True,
                                  position=Vector2(math.sin(self.bubble_time_left * 40) * 16, -10))
                new.addComponent(Destroy(4))
            self.bubble_time_left -= fpsDelta

    def late_update(self, fpsDelta):
        pass

    def b(self):
        if self.bubble_time_left <= 0:
            self.bubble_time_left = self.bubble_time

