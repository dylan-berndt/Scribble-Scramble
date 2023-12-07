from Crash import *
import random


class ConfettiGroup(pyglet.graphics.Group):
    def __init__(self, batch, order=0, parent=None, amount=200):
        self.program = Shader("Shaders/Bad Confetti", sprite_vert=False)
        self._time = 0

        color_file = open(os.path.join(Resources.resourcePath, "resurrect-64.gpl"), "r")
        colors = []
        for line in color_file.readlines()[1:]:
            if line[0] == "#":
                continue

            new_color = [int(num) for num in line.split("\t")[0:3]] + [255]
            colors.append(new_color)

        super().__init__(order, parent)

        c = []
        p = []

        for i in range(amount):
            color = colors[i % len(colors)]
            for g in range(4):
                c.append(color[g])
            p.append((0.5 + 0.1 * i / amount) * 1920)
            p.append((0.2 - 0.4 * i / amount) * 1080)

        self.vertex_list = self.program.vertex_list(amount, GL_POINTS, batch=batch, group=self,
                                                    colors=('Bn', c * amount))
        self.vertex_list.position[:] = p

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, t):
        self.program["iTime"] = t
        self._time = t

    def set_state(self):
        self.program.use()

    def unset_state(self):
        self.program.stop()


class Confetti1(Component):
    def __init__(self, batch, order, parent, amount):
        self.run = False
        self.group = ConfettiGroup(batch, order, parent, amount)

        super().__init__()

    def destroy(self):
        self.group.vertex_list.delete()

    def update(self, fpsDelta):
        if self.run:
            self.group.time += fpsDelta

    def start(self):
        self.group.time = 0
        self.run = True


class Confetti(Component):
    def __init__(self, shader):
        self.run = False
        self.time = 0
        self.program = shader

        super().__init__()

    def update(self, fpsDelta):
        if self.run:
            self.time += fpsDelta
            self.program["iTime"] = self.time

    def start(self):
        self.time = 0
        self.program["iTime"] = self.time
        self.run = True


