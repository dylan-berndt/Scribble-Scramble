import pyglet.image
import cv2

from Crash import *


class Canvas(Component):
    def __init__(self, size, scale, draw=True):
        self.tried = 0
        self.gameObject = None

        self.data = (np.ones([i // scale for i in size] + [4]) * 255).astype('uint8')
        self._image = ArrayImage(size)

        self.anchor = None
        self.size = size
        self.scale = scale

        self.can_draw = draw

        self.tool = "brush"
        self.brush_size = 4
        self.color = [232, 59, 59, 255]
        self.cursor_image = None
        self.cursor_mask = None
        self.brush_image = None
        self.brush_mask = None
        self.brush_color = [232, 59, 59, 255]
        self.brush(self.brush_size, self.color)

        self.mouse = Vector2(0, 0)
        self.cursor = None

        self.points = []

    def on_mouse_click(self, x, y, button, modifiers):
        self.draw_at(x, y, 1, 0, button)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse = Vector2(x, y)
        self.draw_at(x, y, dx, dy, button)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse = Vector2(x, y)

    def mouse_to_canvas(self, x, y):
        size = self.brush_image.shape[0] // 2
        return int(x - self.anchor.x) // self.scale - size, (y - self.anchor.y) // self.scale - size

    def draw_at(self, x, y, dx, dy, button):
        if self.can_draw and button & pyglet.window.mouse.LEFT and self.anchor is not None:
            x, y = int(x - self.anchor.x), int(y - self.anchor.y)

            size = self.brush_image.shape[0] // 2

            gx, gy = x // self.scale - size, y // self.scale - size
            gp = Vector2(gx, gy)

            if not self.points:
                self.points.append(gp)
            else:
                d = gp - self.points[-1]
                distance = d.x ** 2 + d.y ** 2
                if distance > 36:
                    self.points.append(gp)

            if self.tool == "bucket":
                if dx == 1 and dy == 0:
                    self.bucket_at(x // self.scale, y // self.scale)
            else:
                iterations = abs(dx) + abs(dy)

                for i in range(iterations):
                    ix, iy = x - dx * (i / iterations), y - dy * (i / iterations)
                    px, py = int(ix) // self.scale - size, int(iy) // self.scale - size
                    self.brush_at(px, py)

    def bucket_at(self, x, y):
        if x < 0 or y < 0:
            return
        if x >= self.size[0] // self.scale or y >= self.size[1] // self.scale:
            return
        if self.data[y, x].tolist() == self.brush_color:
            return
        check = [(x, y)]
        color = self.data[y, x].tolist()
        while check:
            cx, cy = check[0][0], check[0][1]
            self.check_bucket(cx + 1, cy, color, check)
            self.check_bucket(cx, cy + 1, color, check)
            self.check_bucket(cx - 1, cy, color, check)
            self.check_bucket(cx, cy - 1, color, check)
            del check[0]

    def check_bucket(self, x, y, color, check):
        if x < 0 or y < 0:
            return
        if x >= self.size[0] // self.scale or y >= self.size[1] // self.scale:
            return
        if self.data[y, x].tolist() == color:
            self.data[y, x] = self.brush_color
            check.append((x, y))

    def brush_at(self, x, y, data=None, brush=None, mask=None):
        brush = brush if brush is not None else self.brush_image
        mask = mask if mask is not None else self.brush_mask
        data = data if data is not None else self.data
        x, y = int(x), int(y)
        size = brush.shape[0]
        top_bound = self.size[1] // self.scale - size
        right_bound = self.size[0] // self.scale - size
        tb, rb = max(0, y - top_bound), max(0, x - right_bound)
        bb, lb = min(0, y), min(0, x)
        tb, rb = min(size, tb), min(size, rb)
        bb, lb = max(-size, bb), max(-size, lb)
        start = data[y-bb: y + size - tb, x-lb: x + size - rb]
        try:
            start = np.bitwise_and(start, mask[-bb: size - tb, -lb: size - rb])
        except ValueError:
            print(start.shape, bb, tb, lb, rb, x, y)
        start = np.bitwise_or(start, brush[-bb: size - tb, -lb: size - rb])
        data[y-bb: y + size - tb, x-lb: x + size - rb] = start
        return data

    def update(self, fpsDelta=None):
        data = self.data.copy()

        if self.anchor is not None and self.can_draw:
            size = Vector2(self.brush_image.shape[0], self.brush_image.shape[0])
            mouse = self.mouse - self.anchor
            if self.in_bounds(mouse.x, mouse.y):
                mouse = mouse // self.scale - size // 2
                data = self.brush_at(mouse.x, mouse.y, data, self.cursor_image, self.cursor_mask)

        self._image.array = cv2.resize(data, self.size, interpolation=cv2.INTER_NEAREST)
        self._image.update()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.BRACKETRIGHT:
            size = min(11, self.brush_image.shape[0] // 2 + 1)
            self.brush(size, self.color)
            self.brush_size = size
        if symbol == key.BRACKETLEFT:
            size = max(1, self.brush_image.shape[0] // 2 - 1)
            self.brush(size, self.color)
            self.brush_size = size

    def in_bounds(self, x, y):
        if -1 < x < self.size[0]:
            if -1 < y < self.size[1]:
                return True
        return False

    def blit(self):
        if self.gameObject is not None:
            transform = self.gameObject.transform
            pos = transform.worldToScreen(transform.position)
            anchor = pos - Vector2(self.size[0] // 2, self.size[1] // 2)
            self.anchor = anchor
            self._image.image.blit(anchor.x, anchor.y)

    def change_tool(self, name):
        self.tool = name
        if name == "eraser":
            self.brush(self.brush_size, [255, 255, 255, 255])
        if name == "pencil":
            self.brush(1, [0, 0, 0, 255])
        if name == "brush":
            self.brush(self.brush_size, self.brush_color)
        if name == "bucket":
            self.brush(1, self.brush_color)

    def change_color(self, color):
        self.brush_color = color
        if self.tool != "bucket":
            self.change_tool("brush")

    def brush(self, size, color):
        self.brush_image = np.zeros((size * 2, size * 2, 4), dtype=np.uint8)
        self.brush_mask = np.zeros((size * 2, size * 2, 4), dtype=np.uint8)
        self.cursor_image = np.zeros((size * 2, size * 2, 4), dtype=np.uint8)
        self.cursor_mask = np.zeros((size * 2, size * 2, 4), dtype=np.uint8)
        for by in range(0, size * 2):
            for bx in range(0, size * 2):
                if (bx - size) ** 2 + (by - size) ** 2 < size ** 2:
                    self.cursor_image[bx, by] = [0, 0, 0, 255]
                    self.brush_image[bx, by] = color
                    self.brush_mask[bx, by] = [0, 0, 0, 255]
                    if (bx - size) ** 2 + (by - size) ** 2 < (size - 1) ** 2:
                        self.cursor_mask[bx, by] = [255, 255, 255, 255]
                else:
                    self.cursor_mask[bx, by] = [255, 255, 255, 255]
                    self.brush_mask[bx, by] = [255, 255, 255, 255]
        self.color = color


class ArrayImage:
    def __init__(self, size):
        self.size = size

        self._array_norm = np.ones(self.size + [4], dtype=np.uint8) * 255
        self._tex_data = (pyglet.gl.GLubyte * self._array_norm.size).from_buffer(self._array_norm)

        format_size = 4
        bytes_per_channel = 1
        self.pitch = self.size[0] * format_size * bytes_per_channel
        self.image = pyglet.image.ImageData(self.size[0], self.size[1], "RGBA", self._tex_data)
        self._update_image()

    @property
    def array(self):
        return self._array_norm

    @array.setter
    def array(self, array):
        self._array_norm = array

    def update(self):
        self._update_image()

    def _update_image(self):
        self._tex_data = (pyglet.gl.GLubyte * self._array_norm.size).from_buffer(self._array_norm)
        self.image.set_data("RGBA", self.pitch, self._tex_data)
