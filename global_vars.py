import pyglet
import pymunk
import json
from pyglet.window import key
import constants

space = pymunk.Space()
space.gravity = (0, 0)

with open('client_config.json', encoding='utf-8') as file:
    config = json.load(file)

PORT = config["port"]
host = config["host"]
number_tile_x = config["number_tile_x"]
number_tile_y = config["number_tile_y"]
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
gui_batch = pyglet.graphics.Batch()

projectiles = dict()
tanks = dict()
projectile_count = 0
effect_count = 0
effects = dict()
