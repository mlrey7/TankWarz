import pyglet
import pymunk
from pyglet.window import key
from pyglet import clock
import math
from math import degrees
from math import sin
from math import cos
from enum import Enum
from enum import IntEnum
import random
from opensimplex import OpenSimplex
import constants

space = pymunk.Space()
space.gravity = (0, 0)

window = pyglet.window.Window(width = constants.Game.WIDTH, height = constants.Game.HEIGHT)
keys = key.KeyStateHandler()
window.push_handlers(keys)
bg_group = pyglet.graphics.OrderedGroup(0)
tracks_group = pyglet.graphics.OrderedGroup(1)
tank_group = pyglet.graphics.OrderedGroup(2)
smoke_group = pyglet.graphics.OrderedGroup(3)
barrel_group = pyglet.graphics.OrderedGroup(4)
hud_group = pyglet.graphics.OrderedGroup(5)
bg_batch = pyglet.graphics.Batch()
fg_batch = pyglet.graphics.Batch()
tank_batch = pyglet.graphics.Batch()
barrel_batch = pyglet.graphics.Batch()
projectiles = dict()
tanks = dict()
projectile_count = 0
smoke_count = 0
effects = dict()

