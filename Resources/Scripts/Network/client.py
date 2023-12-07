import socket
from Crash import *
from Resources.Scripts.Network.message import *


class Client(Component):
    def __init__(self, HOST, PORT):
        self.gameObject = None

        self.HOST = HOST
        self.PORT = PORT
        self.SESSION = None
        self.SOCK = None

        self.SID = Game.steam.Users.GetSteamID()

        self.ping_time = 0

        self.connected = False
        self.keep_trying = False

        self.hosting = False

        self.ID = None

        self.users = {}
        self.host = Host(self)

        self.request_time = 2

        self.user_data = None

    def update(self, fpsDelta):
        if self.keep_trying:
            self.connect()

        if not self.connected:
            return

        if self.ping_time <= 0:
            self.ping_time = 1.5
            self.send("PNG")
        self.ping_time -= fpsDelta
        data = self.receive()

        if data:
            self.handle_input(data)

        if self.hosting:
            self.host.update(fpsDelta)

        for user_name in self.users:
            user = self.users[user_name]
            if not user.active:
                if self.request_time <= 0:
                    self.send("REQ||" + user_name)
                    self.request_time = 2

        self.request_time -= fpsDelta

        canvas = self.user_data.canvas

        if canvas is None:
            if GameObject.find("canvas") is not None:
                self.user_data.canvas = GameObject.find("canvas").getComponent("Canvas")
            return

        if len(canvas.points) > 0:
            self.send_points()

    def connect(self):
        if Resources.sceneName != "Scenes/play":
            self.keep_trying = False
            return
        self.SESSION = GameObject.find("password_box").getComponent(TextWidget).document.text
        if self.SESSION == "":
            return

        hosting = GameObject.find("host_check").getComponent("Checkbox").checked
        self.hosting = hosting

        user_name = Game.steam.Friends.GetPlayerName().decode("utf-8")
        self.user_data = User(user_name, str(self.SID))

        self.user_data.face = Game.settings["game"]["character"]["face"]
        self.user_data.hat = Game.settings["game"]["character"]["hat"]
        self.user_data.color = Game.settings["game"]["character"]["color"]

        Game.saveSettings()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.001)

        try:
            s.connect((self.HOST, self.PORT))
            self.SOCK = s
            self.send(str(self.SID) + "//" + self.SESSION + "//h" + ("ost" * hosting), True)
            self.keep_trying = False
            message = self.receive(True)
            self.handle_input(message)

        except socket.timeout:
            self.keep_trying = True

        if self.connected:
            s.setblocking(False)
            loadScene("Scenes/lobby")
        elif not GameObject.find("load_circle") and self.keep_trying:
            circle = GameObject(Vector2(-11, 2), "load_circle")
            renderer = Sprite("Sprites/UI/Load/loading1.png")
            circle.addComponent(renderer)
            load = animation_from_folder("Sprites/UI/Load/", renderer, 12)
            circle.addComponent(Animator({"idle": load}, "idle"))

    def disconnect(self):
        self.connected = False
        self.keep_trying = False
        self.SOCK.close()
        loadScene("Scenes/play")

    def send(self, message, explicit=False):
        message = message.replace("(+)", "")
        if not self.check_socket() and not explicit:
            return
        self.SOCK.send(bytes("(+)" + message, "utf-8"))

    def receive(self, explicit=False):
        if not self.check_socket() and not explicit:
            return
        try:
            data = self.SOCK.recv(2048).decode("utf-8")
            if data:
                print('Received', repr(data))
                return data
        except BlockingIOError:
            pass
        except ConnectionAbortedError:
            self.connected = False
            self.check_socket()
        except socket.timeout:
            pass

    def check_socket(self):
        if not self.connected:
            if Resources.sceneName == "Scenes/lobby" or Resources.sceneName == "Scenes/game":
                loadScene("Scenes/play")
        return self.connected

    def handle_input(self, message):
        if not message:
            return

        split = message.split("(+)")

        for message in split:
            if message:
                self.process_message(message)
                if self.hosting:
                    self.host.process_message(message)

    def process_message(self, message):
        message = message.split("||")

        if message[0].isdigit():
            if not hasattr(self, message[1]):
                return
            process = getattr(self, message[1])
            try:
                process(message[0], message[2])
            except IndexError:
                try:
                    process(message[0])
                except TypeError:
                    process()
        else:
            if not hasattr(self, message[0]):
                return
            process = getattr(self, message[0])
            try:
                process(message[1])
            except IndexError:
                process()

    def on_mouse_click(self, x, y, button, modifiers):
        if self.user_data is None:
            return

        if self.user_data.canvas is None:
            return

        if button & pyglet.window.mouse.LEFT:
            canvas = self.user_data.canvas
            size = canvas.brush_image.shape[0]
            color = canvas.color if canvas.tool in ["pencil", "eraser"] else canvas.brush_color
            string = '{"tool": "%s", "color": %s, "size": %s}'
            self.send((str(self.ID) + "||") * self.hosting + "BBG||" + string %
                      (canvas.tool, color, size))

    def on_mouse_release(self, x, y, button, modifiers):
        if self.user_data is None:
            return

        if self.user_data.canvas is None:
            return

        if button & pyglet.window.mouse.LEFT:
            canvas = self.user_data.canvas

            if canvas is not None:
                if canvas.points:
                    self.send_points()

            self.send((str(self.ID) + "||") * self.hosting + "BED||" + '{}')

    def CNC(self, addr, message=None):
        self.connected = True
        self.ID = addr

    def DNC(self):
        if GameObject.find("load_circle"):
            destroy(GameObject.find("load_circle"))
        self.connected = False

    def JYN(self, addr, message):
        if addr not in self.users and addr != self.ID:
            name = Game.steam.Friends.GetFriendPersonaName(int(message))
            self.users[addr] = User(name.decode('utf-8'), message)
            if self.hosting:
                self.send(str(self.ID) + "||JYN||" + str(self.SID))

    def REQ(self, addr, message=None):
        if addr == self.ID:
            self.send("USR||" + self.user_data.compressed)

    def USR(self, addr, message):
        if addr != self.ID:
            self.users[addr].active = True
            data = json.loads(message)
            self.users[addr].hat = data["hat"]
            self.users[addr].color = data["color"]
            self.users[addr].face = data["face"]

    def MSG(self, addr, message):
        message = password_decrypt(bytes(message, 'utf-8'), self.SESSION).decode()

        chat_log = GameObject.find("chat_log").getComponent(TextWidget)
        doc = chat_log.document

        doc.insert_text(len(doc.text), " ")
        user_name = Game.steam.Friends.GetPlayerName().decode("utf-8")
        user_name = user_name if addr == self.ID else self.users[addr].name
        doc.insert_text(len(doc.text) - 1, user_name + ": " + message + "\n")

    def DEL(self, addr):
        if addr in self.users:
            self.users.pop(addr)

    def BBG(self, addr, message):
        if addr == self.ID:
            return

        draw_data = json.loads(message)

        canvas = self.users[addr].canvas

        if canvas is None:
            return

        canvas.points = []

        canvas.change_tool(draw_data["tool"])
        canvas.brush(max(1, math.ceil(draw_data["size"] / 4.0)), draw_data["color"])
        canvas.brush_color = draw_data["color"]

    def PNT(self, addr, message):
        if addr == self.ID:
            return

        canvas = self.users[addr].canvas

        if canvas is None:
            return

        split = message.split(",")
        x_p, y_p = split[::2], split[1::2]
        points = [canvas.points[-1]] if canvas.points else []
        points += [Vector2(int(x_p[i]) // 2, int(y_p[i]) // 2) for i in range(len(x_p))]

        if canvas.tool == "bucket":
            canvas.bucket_at(points[0].x, points[0].y)
            return

        canvas.brush_at(points[0].x, points[0].y)

        for p, point in enumerate(points[:-1]):
            next_point = points[p + 1]
            d = point - next_point
            iterations = abs(d.x) + abs(d.y)
            for i in range(iterations):
                ix, iy = point.x - d.x * (i / iterations), point.y - d.y * (i / iterations)
                ix, iy = int(ix), int(iy)
                canvas.brush_at(ix, iy)

        canvas.points.append(points[-1])

    def BED(self, addr, message):
        if addr == self.ID:
            return

        canvas = self.users[addr].canvas

        if canvas is None:
            return

        canvas.points = []

    def send_chat(self, message):
        message = message.replace("||", "")
        message = message.replace("(+)", "")

        token = password_encrypt(bytes(message, 'utf-8'), self.SESSION).decode()

        self.send(((str(self.ID) + "||") * self.hosting) + "MSG||" + token)

        if self.hosting:
            chat_log = GameObject.find("chat_log").getComponent(TextWidget)
            doc = chat_log.document
            user_name = Game.steam.Friends.GetPlayerName().decode("utf-8")
            doc.insert_text(len(doc.text), " ")
            doc.insert_text(len(doc.text) - 1, user_name + ": " + message + "\n")

    def send_points(self):
        canvas = self.user_data.canvas
        point_string = ",".join(str(item) for item in canvas.points)
        point_string = point_string.replace("[", "").replace("]", "").replace(" ", "")
        self.send((str(self.ID) + "||") * self.hosting + "PNT||" + point_string)
        canvas.points = []


class Host:
    def __init__(self, client):
        self.client = client

        self.timer = 2 * 60
        self.time = 0

    def update(self, fpsDelta):
        lost_users = []
        for user_addr, user in self.client.users.items():
            user.timeout += fpsDelta
            if user.timeout > 6:
                lost_users.append(user_addr)

        for user_addr in lost_users:
            self.drop_user(user_addr)

    def process_message(self, message):
        message = message.split("||")
        if message[0] in self.client.users:
            self.client.users[message[0]].timeout = 0

            if not hasattr(self, message[1]):
                return
            process = getattr(self, message[1])
            if len(message) > 2:
                process(message[0], message[2])
            else:
                process(message[0])
        elif message[0] != self.client.ID:
            pass

    def drop_user(self, user_addr):
        del self.client.users[user_addr]
        self.client.send(user_addr + "||" + "DEL")

    def MSG(self, addr, message=None):
        self.client.send(addr + "||MSG||" + message)

    def JYN(self, addr, message=None):
        for user in self.client.users:
            self.client.send(user + "||JYN||" + self.client.users[user].sid)

    def REQ(self, addr, message=None):
        if message != self.client.ID:
            self.client.send(message + "||USR||" + self.client.users[message].compressed)
        else:
            self.client.send(message + "||USR||" + self.client.user_data.compressed)

    def BBG(self, addr, message):
        self.client.send(addr + "||BBG||" + message)

    def PNT(self, addr, message):
        self.client.send(addr + "||PNT||" + message)


class User:
    def __init__(self, name, sid):
        self.name = name

        self.sid = sid

        self.color = 0
        self.hat = 0
        self.face = 0

        self.timeout = 0

        self.active = False

        self.canvas = None

    @property
    def compressed(self):
        return '{"face": %s, "hat": %s, "color": %s}' % (self.face, self.hat, self.color)

