from Crash import *


class CharacterManager(Component):
    def __init__(self):
        settings_hat = Game.settings["game"]["character"]["hat"]
        settings_fac = Game.settings["game"]["character"]["face"]
        settings_col = Game.settings["game"]["character"]["color"]

        self.hat_choice = Selection(Vector2(4.5, 4.5), sections=[3, 3], spriteFolder="Sprites/Characters/Hats/")
        self.fac_choice = Selection(Vector2(3.0, 3.0), sections=[2, 2], spriteFolder="Sprites/Characters/Faces/")
        self.col_choice = Selection(Vector2(1.5, 1.5), sections=[1, 1], spriteFolder="Sprites/Characters/Colors/",
                                    dir="V")
        self.hat_choice.choice, self.fac_choice.choice, self.col_choice.choice = \
            settings_hat, settings_fac, settings_col

        GameObject(Vector2(-7.25, 0), "hat_button").addComponent(self.hat_choice)
        GameObject(Vector2(8.75 + 1 / 16, 0.75 + 1 / 16), "face_button").addComponent(self.fac_choice)
        GameObject(Vector2(2.25, 4.5), "color_button").addComponent(self.col_choice)

        batch, group1 = Screen.get_render_set("default", 10)
        batch, group2 = Screen.get_render_set("default", 11)
        batch, group3 = Screen.get_render_set("default", 12)

        self.hat_items = images_from_folder("Sprites/Characters/Hats/")
        self.fac_items = images_from_folder("Sprites/Characters/Faces/")
        self.col_items = images_from_folder("Sprites/Characters/Colors/")

        self.fac_show = Sprite(self.fac_items[settings_fac], batch=batch, group=group2)
        self.hat_show = Sprite(self.hat_items[settings_hat], batch=batch, group=group3)
        self.col_show = Sprite(self.col_items[settings_col], batch=batch, group=group1)

        GameObject(Vector2(0.25, 0), "hat_show").addComponent(self.hat_show)
        GameObject(Vector2(0.25, 0), "fac_show").addComponent(self.fac_show)
        GameObject(Vector2(0.25, 0), "col_show").addComponent(self.col_show)

        self.pos = Vector2(0, 0)
        self.size = Vector2(0, 0)

    def update(self, fpsDelta):
        back = GameObject.find("back_pipes")
        grass = GameObject.find("grass")
        size = Vector(Screen.canvas.get_size())
        position = ((size / 2) - self.pos) / size
        position *= 2
        # back.transform.position = position * -1
        # grass.transform.position = position

    def on_mouse_motion(self, x, y, dx, dy):
        self.pos = Vector2(x, y)

    def choice_update(self):
        Game.settings["game"]["character"]["face"] = self.fac_choice.choice
        Game.settings["game"]["character"]["hat"] = self.hat_choice.choice
        Game.settings["game"]["character"]["color"] = self.col_choice.choice

        self.fac_show.image = self.fac_items[min(len(self.fac_items) - 1, self.fac_choice.choice)]
        self.col_show.image = self.col_items[min(len(self.col_items) - 1, self.col_choice.choice)]
        self.hat_show.image = self.hat_items[min(len(self.hat_items) - 1, self.hat_choice.choice)]

    def face_left(self):
        self.fac_choice.page_down()

    def face_right(self):
        self.fac_choice.page_up()

    def color(self):
        self.col_choice.page_up()

    def hat_left(self):
        self.hat_choice.page_down()

    def hat_right(self):
        self.hat_choice.page_up()


class Selection(Button):
    def __init__(self, size, spriteFolder, sections=None, dir="H"):
        super().__init__(size, function=self.choose)
        self.sections = sections if sections is not None else [1, 1]
        self.x, self.y = 0, 0
        self.choice = 0

        self.page = 0

        batch, group = Screen.get_render_set("default", 10)
        self.scissor = ScissorGroup(Vector2(0, 0), Vector2(1.5, 1.5) * Vector2(sections[0], sections[1]),
                                    order=10 + sections[0])
        self.items = sprites_from_folder(spriteFolder)
        for sprite in self.items:
            sprite.group = self.scissor
            sprite.batch = batch

        self.selection = Sprite("Sprites/Characters/selection.png", batch=batch, group=self.scissor)

        self.scroll_length = 0.4
        self.scroll_time = 0

        self.dir = dir

        self.countdown = 0.1

    def destroy(self):
        self.selection.destroy()
        for sprite in self.items:
            sprite.destroy()

    def on_mouse_click(self, x, y, button, modifiers):
        if button & pyglet.window.mouse.LEFT:
            self.x, self.y = x, y
            super().on_mouse_click(x, y, button, modifiers)

    def update(self, fpsDelta):
        self.countdown -= fpsDelta

        transform = self.gameObject.transform
        self.scissor.position = transform.position

        if self.scroll_time != 0:
            if fpsDelta > abs(self.scroll_time):
                self.scroll_time = 0
            else:
                if abs(self.scroll_time) > self.scroll_time:
                    self.scroll_time += fpsDelta
                else:
                    self.scroll_time -= fpsDelta

        for i in range(len(self.items)):
            sprite = self.items[i]
            page_size = Vector2(1.5 * self.sections[0], 1.5 * self.sections[1])

            dir = Vector2(self.dir == "H", self.dir == "V")

            transition = self.scroll_time / self.scroll_length
            transition = (sine_ease(transition) + ease_in_out_cubic(transition)) / 2
            slide = dir * page_size * transition

            total_pages = math.ceil(len(self.items) / (self.sections[0] * self.sections[1]))
            page_index = (i // (self.sections[0] * self.sections[1]))
            page_num = ((page_index - self.page + total_pages // 2) % total_pages) - total_pages // 2

            choice_position = page_size * dir * page_num
            if self.dir == "H":
                x_add = ((i % self.sections[0]) * 1.5) - 1.5
                y_add = (((i // self.sections[1]) % self.sections[1]) * -1.5) + 1.5
                choice_position += Vector2(x_add, y_add)

            offset = Vector2(0.75 if self.sections[0] % 2 == 1 else 0, 0.875 if self.sections[1] % 2 == 1 else 1.5)
            if self.sections[1] % 2 == 1:
                offset.y -= 0.125

            center = transform.position
            pos = transform.worldToScreen(center + slide + choice_position - offset)

            sprite.x, sprite.y = pos.x, pos.y

            if self.choice == i:
                self.selection.x, self.selection.y = pos.x, pos.y

    def page_up(self):
        self.page = (self.page + 1) % math.ceil(len(self.items) / (self.sections[0] * self.sections[1]))
        self.scroll_time = min(self.scroll_length * 3, self.scroll_time + self.scroll_length)

    def page_down(self):
        self.page = (self.page - 1) % math.ceil(len(self.items) / (self.sections[0] * self.sections[1]))
        self.scroll_time = max(-self.scroll_length * 3, self.scroll_time - self.scroll_length)

    def choose(self):
        if self.countdown > 0:
            return

        transform = self.gameObject.transform
        pos = transform.worldToScreen(transform.position)
        size = self.size * Screen.unit
        s_x, s_y = self.x - pos.x + size.x // 2, self.y - pos.y + size.y // 2
        w, h = size.x // self.sections[0], size.y // self.sections[1]
        section_x = s_x // w
        section_y = s_y // h
        page_weight = self.sections[0] * self.sections[1] * self.page
        self.choice = int((self.sections[1] - section_y - 1) * self.sections[0] + section_x + page_weight)
        GameObject.find("pipes").getComponent(CharacterManager).choice_update()
