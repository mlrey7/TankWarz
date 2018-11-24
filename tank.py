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

from projectile import Projectile
from constants import Color
from constants import Coll_Type
from constants import Direction
from global_vars import space
from global_vars import tanks
from global_vars import window
from global_vars import bg_batch
from global_vars import tank_batch
from global_vars import barrel_batch
from global_vars import keys
from global_vars import projectiles
from global_vars import projectile_count

class Tank:
    SCALE = 0.65
    HEIGHT = 78 * math.sqrt(SCALE)
    WIDTH = 83 * math.sqrt(SCALE)
    BARREL_HEIGHT = 58
    BARREL_WIDTH = 24
    BARREL_SPEED = 1
    
    SPEED = 100
    def __init__(self, pos = (0, 0), color=Color.RED, idn=0):
        self.barrel_batch = barrel_batch
        self.tank_batch = tank_batch
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
        p.body.angle = self.barrelBody.angle
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