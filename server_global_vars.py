import pyglet
import pymunk
from pyglet.window import key
import constants

space = pymunk.Space()
space.gravity = (0, 0)

number_tile_x = 60
number_tile_y = 60
full_width = number_tile_x * 50
full_height = number_tile_y* 50

keys = key.KeyStateHandler()

projectiles = dict()
tanks = dict()
projectile_count = 0
effect_count = 0
effects = dict()

