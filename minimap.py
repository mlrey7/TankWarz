import pyglet
import math
import random
from opensimplex import OpenSimplex
from tile import Tile
from global_vars import bg_batch
from global_vars import hud_batch
from global_vars import bg_group
from global_vars import hud_group
from global_vars import hud_batch
from game_map import Game_Map
from math import sqrt
from global_vars import tanks
from global_vars import projectiles
from tank import Tank
from helper import Rectangle
from constants import Game
import global_vars

class Minimap:
    grass_img = pyglet.image.load("res/PNG/Environment/grass_s.png")
    sand_img = pyglet.image.load("res/PNG/Environment/sand_s.png")
    dirt_img = pyglet.image.load("res/PNG/Environment/dirt_s.png")
    temperate_img = pyglet.image.load("res/PNG/Environment/temperate_s.png")
    shrub_img = pyglet.image.load("res/PNG/Environment/shrub_s.png")
    water_img = pyglet.image.load("res/PNG/Environment/water_s.png")
    darkSand_img = pyglet.image.load("res/PNG/Environment/darksand_s.png")
    SCALE = 0.299999

    def __init__(self, game_map, cl_id):
        self.map_matrix = game_map.map_matrix
        self.sprite_matrix = []
        self.tank_list = []
        self.size_x = 250
        self.size_y = 250
        self.factorx = (self.size_x * 1.0 / global_vars.full_width) 
        self.factory = (self.size_y * 1.0 / global_vars.full_height) 
        #self.factor = 62500 * 1.0 / 2250000
        SCALE = self.factorx
        self.cl_id = cl_id
        for x in range(len(self.map_matrix)):
            for y in range(len(self.map_matrix[0])):
                if self.map_matrix[x][y].tile_type == Tile.Type.GRASS:
                    sprite = pyglet.sprite.Sprite(Game_Map.grass_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DIRT:
                    sprite = pyglet.sprite.Sprite(Game_Map.dirt_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite) 
                elif self.map_matrix[x][y].tile_type == Tile.Type.SAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.sand_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.TEMPERATE:
                    sprite = pyglet.sprite.Sprite(Game_Map.temperate_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.SHRUB:
                    sprite = pyglet.sprite.Sprite(Game_Map.shrub_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DARKSAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.darkSand_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.WATER:
                    sprite = pyglet.sprite.Sprite(Game_Map.water_img, x = 0, y = 0, batch = hud_batch, group=hud_group)
                    sprite.scale = SCALE
                    posx = 10 + (round(sprite.width, 0) * x)
                    posy = 10 + (round(sprite.height, 0) * y)
                    sprite.position = posx, posy
                    self.sprite_matrix.append(sprite)
    def update(self):
        for tank in tanks.values():
            rect = Rectangle(10 + (tank.sprite.position[0] * self.factorx), 10 + (tank.sprite.position[1]* self.factory), 5, 5, (255,0,0,255))
            rect.draw()
        for projectile in projectiles.values():
            rect = Rectangle(10 + (projectile.sprite.position[0] * self.factorx), 10 + (projectile.sprite.position[1]* self.factory), 4, 6, (40,40,40,255))
            rect.draw()
        tank = tanks[self.cl_id]
        area_w =  Game.WIDTH * self.factorx
        area_h =  Game.HEIGHT * self.factory
        area_x = 10 + (tank.sprite.position[0] * self.factorx) - (area_w/ 2)
        area_y = 10 + (tank.sprite.position[1]* self.factory) - (area_h/ 2) 
        if area_x < 10:
            area_x = 10
        elif area_x + area_w > 260:
            area_x = 260 - area_w
        if area_y < 10:
            area_y = 10
        elif area_y + area_h > 260:
            area_y = 260 - area_h
        area = Rectangle(area_x, area_y, area_w, area_h, (255,255,255,255), True)
        area.draw()
            

        



