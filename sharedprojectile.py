import pyglet
import pymunk
import legume
import time
import math

from pyglet.window import key
from pyglet import clock

import global_vars
from server_global_vars import space
from server_global_vars import tanks
from server_global_vars import projectiles
from server_global_vars import projectile_count

from constants import Color
from constants import Coll_Type
from constants import Direction
from constants import Game

from enum import IntEnum

from math import degrees
from math import sin
from math import cos
from math import radians
from shared import *

class SharedProjectile:
    SCALE = 0.65
    HEIGHT = 34 * SCALE
    WIDTH = 20 * SCALE
    class Ammo_Type(IntEnum):
        REGULAR = 1
        AP = 2
    def __init__(self, pos = (0,0), color=Color.RED, idn=0, src_idn = 0, client_id = 0, type=Ammo_Type.REGULAR):
        self.idn = idn
        self.src_idn = src_idn
        self.CLIENT_ID = client_id
        self.color = color
        self.type = type
        self.damage = 10
        self.velocity = 1000
        if self.type == SharedProjectile.Ammo_Type.AP:
            self.damage = 100
            self.velocity = 1500
        self.poly = pymunk.Poly.create_box(None, size=(SharedProjectile.HEIGHT,SharedProjectile.WIDTH))
        self.poly.collision_type = Coll_Type.PROJECTILE
        self.poly.idn = self.idn
        self.moment = pymunk.moment_for_poly(25, self.poly.get_vertices())
        self.body = pymunk.Body(25, self.moment, pymunk.Body.DYNAMIC)
        self.poly.body = self.body
        self.body.position = pos
        space.add(self.poly, self.body)

    def update(self, dt):
        pass
    def destroy(self):
        space.remove(self.poly,self.body)

    def create_from_message(message):
        idn = message.id.value
        src_id = message.src_id.value
        position = message.pos_x.value, message.pos_y.value
        rotation = message.rot.value
        projectile_type = message.type.value
        color = Color.from_int(message.color.value)
        client_id =  message.client_id.value
        return SharedProjectile(position, color, idn, src_id, client_id, projectile_type)

    def update_from_message(self, message):
        self.body.position = message.pos_x.value, message.pos_y.value
        self.body.angle = message.rot.value
        self.type = message.type.value
        self.color = Color.from_int(message.color.value)

    def get_message(self):
        message = ProjectileUpdate()
        message.id.value = self.idn
        message.src_id.value = self.src_idn
        message.color.value =  Color.to_int(self.color)
        message.type.value = self.type
        message.pos_x.value = self.body.position[0]
        message.pos_y.value = self.body.position[1]
        message.l_vel_x.value = self.body.velocity[0]
        message.l_vel_y.value = self.body.velocity[1]
        message.rot.value = self.body.angle
        message.client_id.value = self.CLIENT_ID
        return message


            
        
    