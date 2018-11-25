import pyglet
import math
import random
from opensimplex import OpenSimplex
from tile import Tile
from global_vars import bg_batch
from global_vars import fg_batch
from global_vars import bg_group
from global_vars import hud_group
from game_map import Game_Map
from math import sqrt

class Minimap:
    grass_img = pyglet.image.load("res/PNG/Environment/grass_s.png")
    sand_img = pyglet.image.load("res/PNG/Environment/sand_s.png")
    dirt_img = pyglet.image.load("res/PNG/Environment/dirt_s.png")
    temperate_img = pyglet.image.load("res/PNG/Environment/temperate_s.png")
    shrub_img = pyglet.image.load("res/PNG/Environment/shrub_s.png")
    water_img = pyglet.image.load("res/PNG/Environment/water_s.png")
    darkSand_img = pyglet.image.load("res/PNG/Environment/darksand_s.png")
    
    def __init__(self, game_map):
        self.map_matrix = game_map.map_matrix
        self.sprite_matrix = []
        SCALE = 0.299999
        for x in range(len(self.map_matrix)):
            for y in range(len(self.map_matrix[0])):
                if self.map_matrix[x][y].tile_type == Tile.Type.GRASS:
                    sprite = pyglet.sprite.Sprite(Game_Map.grass_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DIRT:
                    sprite = pyglet.sprite.Sprite(Game_Map.dirt_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite) 
                elif self.map_matrix[x][y].tile_type == Tile.Type.SAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.sand_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.TEMPERATE:
                    sprite = pyglet.sprite.Sprite(Game_Map.temperate_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.SHRUB:
                    sprite = pyglet.sprite.Sprite(Game_Map.shrub_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DARKSAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.darkSand_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.WATER:
                    sprite = pyglet.sprite.Sprite(Game_Map.water_img, x = 0, y = 0, batch = fg_batch, group=hud_group)
                    sprite.scale = SCALE
                    sprite.position = 10 + (sprite.width * sqrt(sprite.scale) * x), 10 + (sprite.height * sqrt(sprite.scale) * y)
                    self.sprite_matrix.append(sprite)
        



