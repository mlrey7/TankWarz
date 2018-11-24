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

space = pymunk.Space()
space.gravity = (0, 0)

window = pyglet.window.Window(width = 1280, height = 720)
keys = key.KeyStateHandler()
window.push_handlers(keys)
bg_group = pyglet.graphics.OrderedGroup(0)
tracks_group = pyglet.graphics.OrderedGroup(1)
tank_group = pyglet.graphics.OrderedGroup(2)
barrel_group = pyglet.graphics.OrderedGroup(3)
bg_batch = pyglet.graphics.Batch()
tank_batch = pyglet.graphics.Batch()
barrel_batch = pyglet.graphics.Batch()
projectiles = dict()
tanks = dict()
projectile_count = 0

class Direction(IntEnum):
    FORWARD = 1
    BACKWARD = -1
    RIGHT = 1
    LEFT = -1
class Color(Enum):
    BLACK = "Black"
    BLUE = "Blue"
    GREEN = "Green"
    RED = "Red"
    BEIGE = "Beige"
class Coll_Type(IntEnum):
    TANK = 1
    PROJECTILE = 2
    ENVIRONMENT = 3
class Tile:
    class Type(Enum):
        DIRT = "dirt"
        GRASS = "grass"
        SAND = "sand"
        TEMPERATE = "temperate"
        SHRUB =  "shrub"
        WATER = "water"
        DARKSAND = 'darksand'
    def __init__(self, tile_type):
        self.tile_type = tile_type
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
            for y in range(len(self.map_matrix)):
                if self.map_matrix[x][y].tile_type == Tile.Type.GRASS:
                    sprite = pyglet.sprite.Sprite(Game_Map.grass_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DIRT:
                    sprite = pyglet.sprite.Sprite(Game_Map.dirt_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite) 
                elif self.map_matrix[x][y].tile_type == Tile.Type.SAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.sand_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.TEMPERATE:
                    sprite = pyglet.sprite.Sprite(Game_Map.temperate_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.SHRUB:
                    sprite = pyglet.sprite.Sprite(Game_Map.shrub_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.DARKSAND:
                    sprite = pyglet.sprite.Sprite(Game_Map.darkSand_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite)
                elif self.map_matrix[x][y].tile_type == Tile.Type.WATER:
                    sprite = pyglet.sprite.Sprite(Game_Map.water_img, x = x*Game_Map.grass_img.width, y = y*Game_Map.grass_img.height, batch = bg_batch)
                    self.sprite_matrix.append(sprite)
                
class Map_Gen:
    WIDTH = 100
    HEIGHT = 100

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rng1 = random.Random()
        self.rng2 = random.Random()
        self.gen1 = OpenSimplex(self.rng1.randint(0,1000))
        self.gen2 = OpenSimplex(self.rng2.randint(0,1000))
    def noise1(self, nx, ny):
        a = self.gen1.noise2d(nx, ny) / 2 + 0.5
        return self.gen1.noise2d(nx, ny) / 2 + 0.5
    def noise2(self, nx, ny):
        return self.gen2.noise2d(nx, ny) / 2 + 0.5
    def generate_values(self):
        values = []
        for y in range(self.height):
            values.append([0] * self.width)
            for x in range(self.width):
                nx, ny = x/self.width - 0.5, y/self.height - 0.5
                e = (1.00 * self.noise1( 1 * nx,  1 * ny)
                    + 0.50 * self.noise1( 2 * nx,  2 * ny)
                    + 0.25 * self.noise1( 4 * nx,  4 * ny)
                    + 0.13 * self.noise1( 8 * nx,  8 * ny)
                    + 0.06 * self.noise1(16 * nx, 16 * ny)
                    + 0.03 * self.noise1(32 * nx, 32 * ny))
                e /= (1.00+0.50+0.25+0.13+0.06+0.03)
                e = e ** 2.00
                m = (1.00 * self.noise2( 1 * nx,  1 * ny)
                    + 0.75 * self.noise2( 2 * nx,  2 * ny)
                    + 0.33 * self.noise2( 4 * nx,  4 * ny)
                    + 0.33 * self.noise2( 8 * nx,  8 * ny)
                    + 0.33 * self.noise2(16 * nx, 16 * ny)
                    + 0.50 * self.noise2(32 * nx, 32 * ny))
                m /= (1.00+0.75+0.33+0.33+0.33+0.50)
   
                values[y][x] = (e,m)
        return values
    def biome(self, e, m):     
        if (e < 0.1):
            return Tile.Type.WATER
        if (e < 0.12):
            return Tile.Type.SAND
        if (e > 0.8):
            return Tile.Type.GRASS
        if (e > 0.6):
            if (m < 0.33): 
                return Tile.Type.DARKSAND
            if (m < 0.66): 
                return Tile.Type.SHRUB
            return Tile.Type.DIRT
        if (e > 0.3):
            if (m < 0.16):
                return Tile.Type.SAND
            if (m < 0.50):
                return Tile.Type.DIRT
            if (m < 0.83):
                return Tile.Type.TEMPERATE
            return Tile.Type.TEMPERATE
        if (m < 0.16): 
            return Tile.Type.SAND
        if (m < 0.33): 
            return Tile.Type.GRASS
        if (m < 0.66): 
            return Tile.Type.GRASS
        return Tile.Type.DIRT
    def generate_map(self):
        map = self.generate_values()
        for y in range(self.height):
            for x in range(self.width):
                map[y][x] = Tile(self.biome(*map[y][x]))
        return Game_Map(map)


class Projectile:
    SCALE = 0.65
    DAMAGE = 10
    HEIGHT = 34 * SCALE
    WIDTH = 20 * SCALE
    def __init__(self, pos = (0,0), color=Color.RED, idn=0, src_idn = 0):
        self.idn = idn
        self.src_idn = src_idn
        img = pyglet.image.load("res/PNG/Bullets/bullet%s_outline.png" % color.value)
        img.anchor_x = img.width // 2 
        img.anchor_y = img.height // 2 
        self.sprite = pyglet.sprite.Sprite(img, x = pos[0], y = pos[1], batch = barrel_batch)
        self.sprite.scale = Projectile.SCALE
        self.poly = pymunk.Poly.create_box(None, size=(Projectile.HEIGHT,Projectile.WIDTH))
        self.poly.collision_type = Coll_Type.PROJECTILE
        self.poly.idn = self.idn
        self.moment = pymunk.moment_for_poly(250, self.poly.get_vertices())
        self.body = pymunk.Body(250, self.moment, pymunk.Body.DYNAMIC)
        self.poly.body = self.body
        self.body.position = pos
        space.add(self.poly, self.body)

    def update(self,dt):
        self.sprite.position = self.body.position
        self.sprite.rotation = degrees(self.body.angle)

    def destroy(self):
        self.sprite = None
        space.remove(self.poly,self.body)

class Tank:
    SCALE = 0.65
    HEIGHT = 78 * math.sqrt(SCALE)
    WIDTH = 83 * math.sqrt(SCALE)
    BARREL_HEIGHT = 58
    BARREL_WIDTH = 24
    BARREL_SPEED = 1

    SPEED = 100
    def __init__(self, pos = (0, 0), color=Color.RED, idn=0):
        self.hp = 100
        self.ammo = 10
        self.isReloading = False
        self.sprite = None
        self.barrelSprite = None
        self.color = color
        self.rotating = False
        self.moving = False
        self.idn = idn

        images = [
        pyglet.image.load("res/PNG/tanks/tankSprites/%s/1.png" % (color.value)),
        pyglet.image.load("res/PNG/tanks/tankSprites/%s/2.png" % (color.value)),
        pyglet.image.load("res/PNG/tanks/tankSprites/%s/3.png" % (color.value)),
        pyglet.image.load("res/PNG/tanks/tankSprites/%s/4.png" % (color.value))
        ]
        for i in range(4):
            images[i].anchor_x = images[i].width // 2 
            images[i].anchor_y = images[i].height // 2 

        self.anim = pyglet.image.Animation.from_image_sequence(images, 0.16, True)
        self.img = pyglet.image.load("res/PNG/tanks/tankSprites/%s/1.png" % color.value)
        self.img.anchor_x = self.img.width // 2 
        self.img.anchor_y = self.img.height // 2 
        self.sprite = pyglet.sprite.Sprite(self.img, x = pos[0], y = pos[1], batch = tank_batch)
        self.sprite.scale = Tank.SCALE

        barrelImg = pyglet.image.load("res/PNG/tanks/barrel%s_outline.png" % color.value)
        barrelImg.anchor_x = barrelImg.width // 2 
        barrelImg.anchor_y = (barrelImg.height // 2) - 15
        self.barrelSprite = pyglet.sprite.Sprite(barrelImg, x = pos[0], y = pos[1], batch = barrel_batch)
        self.barrelSprite.scale = Tank.SCALE 
        self.poly = pymunk.Poly.create_box(None, size=(Tank.HEIGHT,Tank.WIDTH), radius=0.1)
        self.poly.collision_type = Coll_Type.TANK
        self.poly.idn = self.idn
        self.moment = pymunk.moment_for_poly(50000, self.poly.get_vertices())
        self.body = pymunk.Body(50000, self.moment, pymunk.Body.DYNAMIC)
        self.poly.body = self.body
        self.body.position = pos

        #self.barrelPoly = pymunk.Poly.create_box(None, size=(Tank.BARREL_HEIGHT,Tank.BARREL_WIDTH))
        points = [(0,0),(0,58),(24,58),(24,0)]
        self.barrelPoly = pymunk.Poly(None, points, transform=(0,0))
        self.barrelMoment = pymunk.moment_for_poly(10, self.barrelPoly.get_vertices(), offset=(0,-10))
        self.barrelBody = pymunk.Body(1, self.barrelMoment, pymunk.Body.DYNAMIC)
        self.barrelPoly.body = self.barrelBody
        self.barrelBody.position = pos

        space.add(self.poly, self.body)
        space.add(self.barrelPoly, self.barrelBody)

    def update(self, dt):
        self.sprite.position = self.body.position
        self.sprite.rotation = degrees(self.body.angle)
        self.barrelBody.position = self.body.position
        self.barrelSprite.position = self.barrelBody.position
        self.barrelSprite.rotation = degrees(self.barrelBody.angle)
        #self.barrelBody.angular_velocity = 0
        #self.body.velocity = (0,0)
        #self.body.angular_velocity = 0
        
    def fire(self):
        posx = self.barrelBody.position[0] + (sin(self.barrelBody.angle) * 50)
        posy = self.barrelBody.position[1] + (cos(self.barrelBody.angle) * 50)
        global projectile_count
        p = Projectile(pos=(posx, posy), color=self.color, idn=projectile_count,src_idn=self.idn)
        p.body.velocity = (1000*sin(self.barrelBody.angle),1000*cos(self.barrelBody.angle))
        p.body.angle = tank.barrelBody.angle
        projectiles[p.idn] = p
        projectile_count+=1
        self.isReloading = True
        def reload(self, idn):
            tanks[idn].isReloading = False
        clock.schedule_once(reload, 1, self.idn)
    def move(self, direction = Direction.FORWARD):
        if not self.moving:
            self.sprite.image = self.anim
            self.moving = True
        self.body.velocity = (direction*Tank.SPEED*sin(self.body.angle),direction*Tank.SPEED*cos(self.body.angle))
    def stop(self):
        if self.moving:
            self.sprite.image = self.img
            self.moving = False
        self.body.velocity = (0,0)
    def rotate(self, direction = Direction.RIGHT):
        if not self.rotating:
            self.rotating = True
        self.body.angular_velocity = 1*direction
    def stopRotating(self):
        if self.rotating:
            self.rotating = False
        self.body.angular_velocity = 0
    def rotateTurret(self, direction):
        self.barrelBody.angular_velocity = Tank.BARREL_SPEED*direction
    def stopRotateTurret(self):
        self.barrelBody.angular_velocity = 0

tank = Tank(pos = (300,300), color = Color.RED)
tanks[tank.idn] = tank
tank2 = Tank(pos = (500,500), color = Color.BLACK, idn=1)
tanks[tank2.idn] = tank2
projectile_tank_handler = space.add_collision_handler(Coll_Type.TANK, Coll_Type.PROJECTILE)
default_coll_handler = space.add_default_collision_handler()
def a_begin(arbiter, space, data):
    return True
default_coll_handler.begin = a_begin
def begin(arbiter, space, data):
    tankShape = arbiter.shapes[0]
    projectileShape = arbiter.shapes[1]
    tank = tanks[tankShape.idn]
    if projectiles.get(projectileShape.idn) is not None:
        projectile = projectiles[projectileShape.idn]
        if projectile.src_idn != tank.idn:
            print(projectile.src_idn)
            tank.hp -= Projectile.DAMAGE
            projectile.destroy()
            projectiles.pop(projectile.idn)
            print(tank.hp)
    return True
def pre_solve(arbiter, space, data):
    return True
def post_solve(arbiter, space, data):
    pass
def separate(arbiter, space, data):
    pass

projectile_tank_handler.begin = begin
projectile_tank_handler.pre_solve = pre_solve
projectile_tank_handler.post_solve = post_solve
projectile_tank_handler.separate = separate
map_gen = Map_Gen(26, 26)
map1 = map_gen.generate_map()
def reroll_map():
    global map1
    for x in range(len(map1.sprite_matrix)):
        map1.sprite_matrix[x].delete()
    map1 = Map_Gen(26,26).generate_map()
@window.event
def on_draw():
    window.clear()
    bg_batch.draw()
    tank_batch.draw()
    barrel_batch.draw()
    if keys[key.Q]:
        tank.rotateTurret(Direction.LEFT)
    elif keys[key.E]:
        tank.rotateTurret(Direction.RIGHT)
    else:
        tank.stopRotateTurret()
    if keys[key.W]:
        print("forward")
        tank.move(Direction.FORWARD)
    elif keys[key.S]:
        print("backward")
        tank.move(Direction.BACKWARD)
    else:
        tank.stop()
    if keys[key.D]:
        tank.rotate(Direction.RIGHT)
    elif keys[key.A]:
        tank.rotate(Direction.LEFT)
    else:
        tank.stopRotating()
    if keys[key.F] and not tank.isReloading:
        tank.fire()
    if keys[key.SPACE]:
        reroll_map()
def update(dt):
    dtt = 1/60
    space.step(dtt)
    for tank in tanks.values():
        tank.update(dtt)
    for p in projectiles.values():
        p.update(dtt)
 
pyglet.clock.schedule_interval(update, 1.0/60)
pyglet.app.run()