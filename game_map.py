import pyglet
import math
import random
import time 
from opensimplex import OpenSimplex
from tile import Tile
from global_vars import bg_batch
from global_vars import fg_batch
from global_vars import bg_group
class Game_Map:
    grass_img = pyglet.image.load("res/PNG/Environment/grass_s.png")
    sand_img = pyglet.image.load("res/PNG/Environment/sand_s.png")
    dirt_img = pyglet.image.load("res/PNG/Environment/dirt_s.png")
    temperate_img = pyglet.image.load("res/PNG/Environment/temperate_s.png")
    shrub_img = pyglet.image.load("res/PNG/Environment/shrub_s.png")
    water_img = pyglet.image.load("res/PNG/Environment/water_s.png")
    darkSand_img = pyglet.image.load("res/PNG/Environment/darksand_s.png")
    def __init__(self, map_matrix):
        self.map_matrix = map_matrix
        self.sprite_matrix = []
        for x in range(len(self.map_matrix)):
            for y in range(len(self.map_matrix[0])):
                if self.map_matrix[x][y].tile_type == Tile.Type.GRASS:
                    sprite = pyglet.sprite.Sprite(Game_Map.grass_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DIRT:
                    sprite = pyglet.sprite.Sprite(Game_Map.dirt_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite) 
                elif self.map_matrix[x][y].tile_type == Tile.Type.SAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.sand_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.TEMPERATE:
                    sprite = pyglet.sprite.Sprite(Game_Map.temperate_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.SHRUB:
                    sprite = pyglet.sprite.Sprite(Game_Map.shrub_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DARKSAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.darkSand_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.WATER:
                    sprite = pyglet.sprite.Sprite(Game_Map.water_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch, group=bg_group)
                    self.sprite_matrix.append(sprite)
    def generate_map(width, height, seed_a, seed_b):
        rng1 = random.Random()
        rng1.seed(seed_a)
        rng2 = random.Random()
        rng2.seed(seed_b)
        gen1 = OpenSimplex(rng1.randint(0,100000))
        gen2 = OpenSimplex(rng2.randint(0,100000))
        def noise1(nx, ny):
            return gen1.noise2d(nx, ny) / 2 + 0.5
        def noise2(nx, ny):
            return gen2.noise2d(nx, ny) / 2 + 0.5
        def generate_values():
            values = []
            for x in range(width):
                values.append([0] * height)
                for y in range(height):
                    nx, ny = x/width - 0.5, y/height - 0.5
                    e = (1.00 * noise1( 1 * nx,  1 * ny)
                        + 0.50 * noise1( 2 * nx,  2 * ny)
                        + 0.25 * noise1( 4 * nx,  4 * ny)
                        + 0.13 * noise1( 8 * nx,  8 * ny)
                        + 0.06 * noise1(16 * nx, 16 * ny)
                        + 0.03 * noise1(32 * nx, 32 * ny))
                    e /= (1.0+0.50+0.25+0.13+0.06+0.03)
                    e = e ** 4
                    e *= 10
                    m = (1.00 * noise2( 1 * nx,  1 * ny)
                        + 0.75 * noise2( 2 * nx,  2 * ny)
                        + 0.33 * noise2( 4 * nx,  4 * ny)
                        + 0.33 * noise2( 8 * nx,  8 * ny)
                        + 0.33 * noise2(16 * nx, 16 * ny)
                        + 0.50 * noise2(32 * nx, 32 * ny))
                    m /= (1.00+0.75+0.33+0.33+0.33+0.50)
                    values[x][y] = (e,m)
            return values
        def biome(e, m):     
            if (e < 0.06):
                return Tile.Type.WATER
            if (e < 0.12):
                return Tile.Type.SAND
            if (e > 0.8):
                if (m < 0.2):
                    return Tile.Type.DARKSAND
                if (m < 0.5):
                    return Tile.Type.GRASS
                if (m < 0.6):
                    return Tile.Type.SHRUB
                return Tile.Type.TEMPERATE
            if (e > 0.6):
                if (m < 0.33): 
                    return Tile.Type.SAND
                if (m < 0.66): 
                    return Tile.Type.GRASS
                return Tile.Type.DIRT
            if (e > 0.3):
                if (m < 0.16):
                    return Tile.Type.SAND
                if (m < 0.50):
                    return Tile.Type.DIRT
                if (m < 0.83):
                    return Tile.Type.GRASS
                return Tile.Type.GRASS
            if (m < 0.16): 
                return Tile.Type.SAND
            if (m < 0.33): 
                return Tile.Type.DIRT
            if (m < 0.66): 
                return Tile.Type.GRASS
            return Tile.Type.DIRT
        map = generate_values()
        for x in range(width):
            for y in range(height):
                map[x][y] = Tile(biome(*map[x][y]))
        return Game_Map(map)

    def create_from_message(message):
        seed_a = message.seed_a.value
        seed_b = message.seed_b.value
        length = message.l.value
        width = message.w.value
        return Game_Map.generate_map(length, width, seed_a, seed_b)