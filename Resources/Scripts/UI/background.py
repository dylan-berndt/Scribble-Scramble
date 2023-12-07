from Crash import *


class Scroll(Component):
    def __init__(self):
        self.gameObject = None

    def update(self, fpsDelta):
        pos = self.gameObject.transform.position
        self.gameObject.transform.position = Vector2(-pos.x % 3, -pos.y % 3) * -1


class Swap(Component):
    def __init__(self, sprite, color):
        self.gameObject = None

        self.sprite = sprite
        self.colors = ["red", "orange", "yellow", "green", "blue", "purple", "white", "black"]
        self.index = self.colors.index(color)

    def update(self, fpsDelta):
        pass

    def swap(self, name):
        image = load_image("Sprites/UI/Background/" + name + ".png")
        self.sprite.image = image
        self.sprite.tile(Vector2(32, 32))

    def left(self, arg):
        self.index = (self.index - 1) % len(self.colors)
        self.swap(self.colors[self.index])

    def right(self, arg):
        self.index = (self.index + 1) % len(self.colors)
        self.swap(self.colors[self.index])
