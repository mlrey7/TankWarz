import pyglet
import pymunk
import legume
import time

from pyglet.window import key
from pyglet import clock

import global_vars
from global_vars import space
from global_vars import tanks
from global_vars import projectiles


from constants import Color
from constants import Coll_Type
from constants import Direction
from constants import Game

from game_map import Game_Map

import collision_handler
from pyglet.gl import Config
from enum import IntEnum

UPDATE_RATE = 1
UPDATES_PER_SECOND = 1.0 / UPDATE_RATE
PORT = 27806

class TankCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+1
    MessageValues = {
        'id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'int',
        'l_vel_y' : 'int',
        'a_vel' : 'int',
        'color' : 'string'}

class TankUpdate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+2
    MessageValues = {
        'id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'int',
        'l_vel_y' : 'int',
        'a_vel' : 'int'}

class TankCommand(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+3
    MessageValues = {
        'id' : 'int',
        'command' : 'int'
    }

class ProjectileCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+4
    MessageValues = {
        'id' : 'int',
        'src_id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'type' : 'int',
        'color' : 'string'}

class ProjectileUpdate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+5
    MessageValues = {
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'int',
        'l_vel_y' : 'int'}

class MapCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+6
    MessageValues = {
        'l' : 'int',
        'w' : 'int',
        'seed_a' : 'float',
        'seed_b' : 'float'}

legume.messages.message_factory.add(TankCreate)
legume.messages.message_factory.add(TankUpdate)
legume.messages.message_factory.add(TankCommand)
legume.messages.message_factory.add(ProjectileCreate)
legume.messages.message_factory.add(ProjectileUpdate)
legume.messages.message_factory.add(MapCreate)

class Tank:
    class Command(IntEnum):
        NOTHING = 0
        MOVE_FORWARD = 1
        MOVE_BACKWARD = 2
        ROTATE_RIGHT = 3
        ROTATE_LEFT = 4
        TURRET_ROTATE_RIGHT = 5
        TURRET_ROTATE_LEFT = 6
        STOP_MOVING = 7
        STOP_ROTATING = 8
        STOP_ROTATING_TURRET = 9
        FIRE = 10
        DESTROY = 11

        def from_int(c):
            return CommandInt[c]

    CommandInt = {
            0 : Command.NOTHING,
            1 : Command.MOVE_FORWARD,
            2 : Command.MOVE_BACKWARD,
            3 : Command.ROTATE_RIGHT,
            4 : Command.ROTATE_LEFT,
            5 : Command.TURRET_ROTATE_RIGHT,
            6 : Command.TURRET_ROTATE_LEFT,
            7 : Command.STOP_MOVING,
            8 : Command.STOP_ROTATING,
            9 : Command.STOP_ROTATING_TURRET,
            11 : Command.FIRE,
            12 : Command.DESTROY
            }
        
    def __init__(self, pos = (0, 0), color=Color.RED, idn=0):
        self.alive = True
        self.hp = 100
        self.ammo1 = 40
        self.ammo2 = 5
        self.isReloading = False
        self.color = color
        self.rotating = False
        self.moving = False
        self.idn = idn
        self.ammo_mode = Projectile.Ammo_Type.REGULAR

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
        self.barrelBody.position = self.body.position

    def fire(self):
        if self.ammo_mode == Projectile.Ammo_Type.REGULAR and self.ammo1 <= 0 or self.ammo_mode == Projectile.Ammo_Type.AP and self.ammo2 <= 0:
            return
        if self.ammo_mode == Projectile.Ammo_Type.REGULAR:
            self.ammo1 -= 1
        elif self.ammo_mode == Projectile.Ammo_Type.AP:
            self.ammo2 -= 1
        posx = self.barrelBody.position[0] + (sin(self.barrelBody.angle) * 50)
        posy = self.barrelBody.position[1] + (cos(self.barrelBody.angle) * 50)
        global projectile_count
        p = Projectile(pos=(posx, posy), color=self.color, idn=projectile_count,src_idn=self.idn, type=self.ammo_mode)
        p.body.velocity = (p.velocity*sin(self.barrelBody.angle),p.velocity*cos(self.barrelBody.angle))
        p.body.angle = self.barrelBody.angle
        projectiles[p.idn] = p
        projectile_count+=1
 
        self.isReloading = True

        def reload(self, idn):
            tanks[idn].isReloading = False
        clock.schedule_once(reload, 2, self.idn)
        
    def move(self, direction = Direction.FORWARD):
        if not self.moving:
            self.moving = True
        self.body.velocity = (direction*Tank.SPEED*sin(self.body.angle),direction*Tank.SPEED*cos(self.body.angle))
    def stop(self):
        if self.moving:
            self.moving = False
        self.body.velocity = (0,0)
    def rotate(self, direction = Direction.RIGHT):
        if not self.moving:
            pass
        if not self.rotating:
            self.rotating = True
        self.body.angular_velocity = 1*direction
    def stopRotating(self):
        if not self.moving:
            pass
        if self.rotating:
            self.rotating = False
        self.body.angular_velocity = 0
    def rotateTurret(self, direction):
        self.barrelBody.angular_velocity = Tank.BARREL_SPEED*direction
    def stopRotateTurret(self):
        self.barrelBody.angular_velocity = 0
    def destroy(self):
        self.alive = False
        pass

    def hit(self):
        pass

    def create_from_message(message):
        idn = message.id.value
        position = message.pos_x.value, message.pos_y.value
        color = Color.from_int[message.color.value]
        return Tank(position, color, idn)
    def update_from_message(self, message):
        self.body.position = message.pos_x.value, message.pos_y.value
        self.body.velocity = message.l_vel_x.value,  message.l_vel_y.value
        self.body.rotation = message.rot.value
        self.body.angular_velocity = message.a_vel.value
    
    def get_message(self):
        message = shared.TankUpdate()
        message.id.value = self.idn
        message.pos_x.value = self.body.position[0]
        message.pos_y.value = self.body.position[1]
        message.l_vel_x.value = self.body.velocity[0]
        message.l_vel_y.value = self.body.velocity[1]
        message.a_vel = self.body.angular_velocity
        return message


class Projectile:
    class Ammo_Type(IntEnum):
        REGULAR = 1
        AP = 2
    def __init__(self, pos = (0,0), color=Color.RED, idn=0, src_idn = 0, type=Ammo_Type.REGULAR):
        self.idn = idn
        self.src_idn = src_idn
        self.type = type
        self.damage = 10
        self.velocity = 1000
        if self.type == Projectile.Ammo_Type.AP:
            self.damage = 100
            self.velocity = 1500
        self.poly = pymunk.Poly.create_box(None, size=(Projectile.HEIGHT,Projectile.WIDTH))
        self.poly.collision_type = Coll_Type.PROJECTILE
        self.poly.idn = self.idn
        self.moment = pymunk.moment_for_poly(25, self.poly.get_vertices())
        self.body = pymunk.Body(25, self.moment, pymunk.Body.DYNAMIC)
        self.poly.body = self.body
        self.body.position = pos
        space.add(self.poly, self.body)

    def destroy(self):
        space.remove(self.poly,self.body)

    def create_from_message(message):
        idn = message.id.value
        src_id = message.src_id.value
        position = message.pos_x.value, message.pos_y.value
        rotation = message.rot.value
        projectile_type = message.type.value
        color = Color.from_int[message.color.value]
        return Projectile(position, color, idn, src_id)

    def update_from_message(self, message):
        self.body.position = message.pos_x.value, message.pos_y.value
        self.body.angle = message.rot.value

    def get_message(self):
        message = shared.ProjectileUpdate()
        message.id.value = self.idn
        message.pos_x.value = self.body.position[0]
        message.pos_y.value = self.body.position[1]
        message.l_vel_x.value = self.body.velocity[0]
        message.l_vel_y.value = self.body.velocity[1]
        return message


