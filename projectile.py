import pyglet
import pymunk
from math import degrees
from constants import Color
from constants import Coll_Type
from constants import Direction
from global_vars import barrel_batch
from global_vars import fg_batch
from global_vars import space
from global_vars import barrel_group
from enum import IntEnum
class Projectile:
    class Ammo_Type(IntEnum):
        REGULAR = 1
        AP = 2
    SCALE = 0.65
    DAMAGE = 10
    HEIGHT = 34 * SCALE
    WIDTH = 20 * SCALE
    def __init__(self, pos = (0,0), color=Color.RED, idn=0, src_idn = 0, type=Ammo_Type.REGULAR):
        self.idn = idn
        self.src_idn = src_idn
        self.type = type
        self.damage = 10
        img = None
        if self.type == Projectile.Ammo_Type.REGULAR:
            img = pyglet.image.load("res/PNG/Bullets/bullet%s_outline.png" % color.value)
        elif self.type == Projectile.Ammo_Type.AP:
            img = pyglet.image.load("res/PNG/Bullets/bullet%sSilver_outline.png" % color.value)
            self.damage = 100
        img.anchor_x = img.width // 2 
        img.anchor_y = img.height // 2 
        self.sprite = pyglet.sprite.Sprite(img, x = pos[0], y = pos[1], batch = fg_batch, group=barrel_group)
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
