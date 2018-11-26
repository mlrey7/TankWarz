import pyglet
import pymunk
from pyglet.window import key
import constants

space = pymunk.Space()
space.gravity = (0, 0)

window = pyglet.window.Window(width = constants.Game.WIDTH, height = constants.Game.HEIGHT)

number_tile_x = 60
number_tile_y = 60
full_width = number_tile_x * 50
full_height = number_tile_y* 50

keys = key.KeyStateHandler()

bg_group = pyglet.graphics.OrderedGroup(0)
tracks_group = pyglet.graphics.OrderedGroup(1)
tank_group = pyglet.graphics.OrderedGroup(2)
smoke_group = pyglet.graphics.OrderedGroup(3)
barrel_group = pyglet.graphics.OrderedGroup(4)
explosion_group = pyglet.graphics.OrderedGroup(5)
hud_group = pyglet.graphics.OrderedGroup(100)
bg_batch = pyglet.graphics.Batch()
fg_batch = pyglet.graphics.Batch()
hud_batch = pyglet.graphics.Batch()
tank_batch = pyglet.graphics.Batch()
barrel_batch = pyglet.graphics.Batch()
projectiles = dict()
tanks = dict()
projectile_count = 0
effect_count = 0
effects = dict()

corner_point = constants.Game.WIDTH, constants.Game.HEIGHT
