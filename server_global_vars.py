import pyglet
import pymunk
from pyglet.window import key
import constants
import json

with open('server_config.json', encoding='utf-8') as file:
    config = json.load(file)

PORT = config["port"]
number_tile_x = config["number_tile_x"]
number_tile_y = config["number_tile_y"]
game_length = config["game_length"]
full_width = number_tile_x * 50
full_height = number_tile_y* 50

space = pymunk.Space()
space.gravity = (0, 0)

keys = key.KeyStateHandler()

projectiles = dict()
tanks = dict()
projectile_count = 0
effect_count = 0
effects = dict()

