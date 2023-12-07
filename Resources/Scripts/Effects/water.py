from Crash import *
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage import sobel
from scipy.signal import fftconvolve


class Water(Component):
    def __init__(self):
        self.texture_scale = 8

        self.size = [Screen.size.y // self.texture_scale, Screen.size.x // self.texture_scale]

        self.pressure = np.zeros(self.size)

        self.distance = 8
        self.weight = 1

        self.height = 40

        self.pitch = self.pressure.shape[1] * 4
        velocity_int = self.pressure.astype(np.uint8)
        velocity_bytes = (pyglet.gl.GLubyte * velocity_int.size).from_buffer(velocity_int)
        self.data = pyglet.image.ImageData(self.pressure.shape[1], self.pressure.shape[0], "RGBA", velocity_bytes)

        r_data = np.zeros([self.distance * 2, self.distance * 2])
        for y in range(self.distance * 2):
            for x in range(self.distance * 2):
                d = ((x - self.distance) ** 2) + ((y - self.distance) ** 2)
                if math.sqrt(d) < self.distance:
                    r_data[y, x] = 1
                # if math.sqrt(d) > self.distance:
                #     r_data[y, x] = 0
                # else:
                #     m = 1 - (math.sqrt(d) / self.distance)
                #     r_data[y, x] = m

        self.brush = r_data

        self.program = None

        self.sprite = None

        self.time = 0

        super().__init__()

    def update(self, fpsDelta):
        if self.sprite is None:
            self.sprite = self.gameObject.getComponent(Sprite)
            self.sprite.scale = self.texture_scale
            self.sprite.program["s"] = self.texture_scale

        self.time += fpsDelta
        self.sprite.program["iTime"] = self.time
        self.sprite.program["WATER_HEIGHT"] = self.height

        # distance = self.velocity[:, :, :2] - 127
        # distance = np.clip(distance, -2, 2)
        # self.velocity[:, :, :2] -= distance
        # self.velocity = np.clip(self.velocity, 0, 255)

        self.pressure = gaussian_filter(self.pressure, [2, 4])
        self.pressure *= 0.99

        # kernel = np.array([[1, 2, 1],
        #                    [2, 4, 2],
        #                    [1, 2, 1]]) / 16
        # p = np.dstack([self.pressure, self.pressure, self.pressure])
        # self.pressure = fftconvolve(p, kernel[:, :, np.newaxis])[:, :, 0]

        # for y in range(1, self.size[0] - 1):
        #     for x in range(1, self.size[1] - 1):
        #         l, r = self.pressure[y, x - 1], self.pressure[y, x + 1]
        #         u, d = self.pressure[y - 1, x], self.pressure[y + 1, x]
        #         self.pressure[y, x] = fpsDelta * (u + d + l + r - 4 * self.pressure[y, x]) + self.pressure[y, x]

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = (x // self.texture_scale) - self.distance, (y // self.texture_scale) - self.distance

        dx, dy = dx // self.texture_scale, dy // self.texture_scale

        iterations = abs(dx) + abs(dy)

        for i in range(iterations):
            ix, iy = x - dx * (i / iterations), y - dy * (i / iterations)
            ix, iy = int(ix), int(iy)

            y_s, y_e = max(0, iy), min(self.size[0], iy + self.distance * 2)
            x_s, x_e = max(0, ix), min(self.size[1], ix + self.distance * 2)

            r = self.brush[y_s - iy:y_e - iy, x_s - ix:x_e - ix]

            self.pressure[y_s:y_e, x_s:x_e] += r * abs(dx) * self.weight
            self.pressure[y_s:y_e, x_s:x_e] += r * abs(dy) * self.weight

    def on_draw(self):
        # s_h, s_v = sobel(self.pressure, 0), sobel(self.pressure, 1)
        # p = np.sqrt(s_h ** 2 + s_v ** 2)
        p = self.pressure
        image = np.dstack([p, p, p])
        image = np.pad(image, ((0, 0), (0, 0), (0, 1)), mode="constant", constant_values=255)

        image_int = np.clip(image, 0, 255).astype(np.uint8)
        image_bytes = (pyglet.gl.GLubyte * image_int.size).from_buffer(image_int)
        self.data.set_data("RGBA", self.pitch, image_bytes)
        texture = self.data.get_texture()
        self.sprite.image = texture

