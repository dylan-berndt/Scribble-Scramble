from Crash import *

# Editor.toggle("steam")

pyglet.font.add_file(Objects.resourcePath + 'GrapeSoda.ttf')
grape_soda = pyglet.font.load('GrapeSoda')
pyglet.font.add_file(Objects.resourcePath + 'GrapePopsicle.ttf')
grape_popsicle = pyglet.font.load('GrapePopsicle')
pyglet.font.add_file(Objects.resourcePath + "Poco.ttf")
poco = pyglet.font.load("Poco")
pyglet.font.add_file(Objects.resourcePath + "Neutrino.ttf")
neutrino = pyglet.font.load("Neutrino")

pyglet.image.Texture.default_min_filter = GL_NEAREST
pyglet.image.Texture.default_mag_filter = GL_NEAREST

Window(Vector2(1920, 1080), "Scribble Scramble", resizable=True, sceneName="Scenes/splash", fullscreen=True)
