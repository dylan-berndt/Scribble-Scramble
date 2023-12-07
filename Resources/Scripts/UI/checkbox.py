from Crash import *


class Checkbox(Component):
    def __init__(self, default_sprite, check_sprite):
        self.gameObject = None

        self.checked = False

        self.check_sprite = check_sprite
        self.default_sprite = default_sprite

    def update(self, fpsDelta):
        pass

    def toggle(self):
        self.checked = not self.checked

        image = self.check_sprite if self.checked else self.default_sprite
        sprite = self.gameObject.getComponent(Sprite)
        if sprite is not None:
            sprite.image = image
