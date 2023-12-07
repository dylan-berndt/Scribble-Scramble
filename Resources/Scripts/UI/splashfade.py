from Crash import *


class SplashFade(Component):
    def __init__(self, renderer, animator):
        self.gameObject = None
        self.renderer = renderer
        self.animator = animator
        self.time = 0

        self.before_fade = 1.0
        self.start_time = 2.0
        self.end_time = 5
        self.fade_time = 2

        self.started = False

    def update(self, fpsDelta):
        self.time += fpsDelta

        if self.time < self.start_time:
            num = 255 * (self.time - self.before_fade) / (self.start_time - self.before_fade)
            self.renderer.opacity = min(255, max(0, num))

        if self.time > self.start_time and not self.started:
            self.animator.play()
            self.started = True

        if self.time > self.end_time:
            num = (self.fade_time - (self.time - self.end_time)) * 255
            self.renderer.opacity = min(255, max(0, num))
            if num < -100:
                loadScene("Scenes/menu")


