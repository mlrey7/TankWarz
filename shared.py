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

from game_map import Game_Map

from pyglet.gl import Config
from enum import IntEnum

from math import degrees
from math import sin
from math import cos
from math import radians

UPDATES_PER_SECOND = 60
UPDATE_RATE = 1.0 / UPDATES_PER_SECOND

PORT = 27806

class TankCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+1
    MessageValues = {
        'id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'float',
        'l_vel_y' : 'float',
        'a_vel' : 'float',
        'color' : 'int',
        'alive' : 'bool'}

class TankUpdate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+2
    MessageValues = {
        'id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'l_vel_x' : 'float',
        'l_vel_y' : 'float',
        'a_vel' : 'float',
        'turret_rot' : 'float',
        'turret_vel' : 'float',
        'color' : 'int',
        'alive' : 'bool'}

class TankCommand(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+3
    MessageValues = {
        'id' : 'int',
        'command' : 'int'
    }

class FakeValues(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+80
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
        'color' : 'int'}

class ProjectileDestroy(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+55
    MessageValues = {
        'projectile_id' : 'int'}
class TankFire(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+50
    MessageValues = {
        'id' : 'int',
        'projectile_id' : 'int'}

class TankHit(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+53
    MessageValues = {
        'id' : 'int',
        'projectile_id' : 'int'}

class TankFireClient(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+51
    MessageValues = {
        'id' : 'int',
        'projectile_id' : 'int'}

class TankSwitchAmmo(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+56
    MessageValues = {
        'id' : 'int',
        'ammo_type' : 'int'}

class ProjectileUpdate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+5
    MessageValues = {
        'id' : 'int',
        'src_id' : 'int',
        'pos_x' : 'float',
        'pos_y' : 'float',
        'rot' : 'float',
        'color' : 'int',
        'type' : 'int',
        'l_vel_x' : 'float',
        'l_vel_y' : 'float'}

class MapCreate(legume.messages.BaseMessage):
    MessageTypeID = legume.messages.BASE_MESSAGETYPEID_USER+6
    MessageValues = {
        'l' : 'int',
        'w' : 'int',
        'seed_a' : 'int',
        'seed_b' : 'int'}

legume.messages.message_factory.add(TankCreate)
legume.messages.message_factory.add(TankUpdate)
legume.messages.message_factory.add(TankCommand)
legume.messages.message_factory.add(ProjectileCreate)
legume.messages.message_factory.add(ProjectileUpdate)
legume.messages.message_factory.add(MapCreate)
legume.messages.message_factory.add(FakeValues)
legume.messages.message_factory.add(TankFire)
legume.messages.message_factory.add(TankFireClient)
legume.messages.message_factory.add(TankHit)
legume.messages.message_factory.add(ProjectileDestroy)
legume.messages.message_factory.add(TankSwitchAmmo)


class FakeSprite:
    def __init__(self, pos=(0,0)):
        self.position = pos
        self.angular_velocity = 0
        self.rotation = 0
class SharedTank:
    SCALE = 0.65
    HEIGHT = 78 * math.sqrt(SCALE)
    WIDTH = 83 * math.sqrt(SCALE)
    BARREL_HEIGHT = 58
    BARREL_WIDTH = 24
    BARREL_SPEED = 1
    SPEED = 100
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
        HIT = 12
        

        def from_int(c):
            return SharedTank.CommandInt[c]

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
            10 : Command.FIRE,
            11 : Command.DESTROY,
            12 : Command.HIT
            
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
        self.ammo_type = SharedProjectile.Ammo_Type.REGULAR
        self.command = SharedTank.Command.NOTHING
        self.poly = pymunk.Poly.create_box(None, size=(SharedTank.HEIGHT,SharedTank.WIDTH), radius=0.1)
        self.poly.collision_type = Coll_Type.TANK
        self.poly.idn = self.idn
        self.moment = pymunk.moment_for_poly(50000, self.poly.get_vertices())
        self.body = pymunk.Body(50000, self.moment, pymunk.Body.DYNAMIC)
        self.poly.body = self.body
        self.body.position = pos


        barrelImg = pyglet.image.load("res/PNG/tanks/barrel%s_outline.png" % color.value)
        barrelImg.anchor_x = barrelImg.width // 2 
        barrelImg.anchor_y = (barrelImg.height // 2) - 15
        self.barrelSprite = FakeSprite((pos[0], pos[1]))
        # self.barrelSprite = pyglet.sprite.Sprite(barrelImg, x = pos[0], y = pos[1])
        # self.barrelSprite.scale = Tank.SCALE 
        # self.barrelSprite.angular_velocity = 0

        # points = [(0,0),(0,58),(24,58),(24,0)]
        # self.barrelPoly = pymunk.Poly(None, points, transform=(0,0))
        # self.barrelMoment = pymunk.moment_for_poly(10, self.barrelPoly.get_vertices(), offset=(0,-10))
        # self.barrelBody = pymunk.Body(1, self.barrelMoment, pymunk.Body.DYNAMIC)
        # self.barrelPoly.sensor = True
        # self.barrelPoly.body = self.barrelBody
        # self.barrelBody.position = pos

        space.add(self.poly, self.body)
        #space.add(self.barrelPoly, self.barrelBody)
    
    def update(self, dt):
        if self.alive:
            self.barrelSprite.position = self.body.position
            self.barrelSprite.rotation += degrees(self.barrelSprite.angular_velocity) * dt

    def fire(self, projectile_id):
        if self.ammo_type == SharedProjectile.Ammo_Type.REGULAR and self.ammo1 <= 0 or self.ammo_type == SharedProjectile.Ammo_Type.AP and self.ammo2 <= 0:
            return
        if self.ammo_type == SharedProjectile.Ammo_Type.REGULAR:
            self.ammo1 -= 1
        elif self.ammo_type == SharedProjectile.Ammo_Type.AP:
            self.ammo2 -= 1
        posx = self.body.position[0] + (sin(radians(self.barrelSprite.rotation)) * 50)
        posy = self.body.position[1] + (cos(radians(self.barrelSprite.rotation)) * 50)
        global projectile_count
        p = SharedProjectile(pos=(posx, posy), color=self.color, idn=projectile_id,src_idn=self.idn, type=self.ammo_type)
        p.body.velocity = (p.velocity*sin(radians(self.barrelSprite.rotation)),p.velocity*cos(radians(self.barrelSprite.rotation)))
        p.body.angle = radians(self.barrelSprite.rotation)
        #print("projectile at start server: ",p.body.angle, "id:", p.idn)
        projectiles[p.idn] = p
        projectile_count+=1
 
        self.isReloading = True

        def reload(self, idn):
            tanks[idn].isReloading = False
        clock.schedule_once(reload, 2, self.idn)
        
    def move(self, direction = Direction.FORWARD):
        if not self.moving and self.alive:
            self.moving = True
        #print("server v,angle", self.body.velocity, degrees(self.body.angle))
        if self.alive:
            self.body.velocity = (direction*SharedTank.SPEED*sin(self.body.angle),direction*SharedTank.SPEED*cos(self.body.angle))
        #print("server v,angle after", self.body.velocity, degrees(self.body.angle))
    def stop(self):
        if self.moving:
            self.moving = False
        self.body.velocity = (0,0)
    def rotate(self, direction = Direction.RIGHT):
        if not self.moving:
            pass
        if not self.rotating and self.alive:
            self.rotating = True
        if self.alive:
            self.body.angular_velocity = 1*direction
    def stopRotating(self):
        if not self.moving:
            pass
        if self.rotating:
            self.rotating = False
        self.body.angular_velocity = 0
    def rotateTurret(self, direction):
        if self.alive:
        #self.barrelBody.angular_velocity = Tank.BARREL_SPEED*direction
            self.barrelSprite.angular_velocity = SharedTank.BARREL_SPEED*direction
    def stopRotateTurret(self):
        #self.barrelBody.angular_velocity = 0
        self.barrelSprite.angular_velocity = 0
    def destroy(self):
        self.alive = False
        space.remove(self.body)
        #self.body.body_type = pymunk.Body.STATIC
        pass

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0 and self.alive:
            self.body.velocity = 0,0
            self.body.angular_velocity = 0
            self.destroy()
        else:
            pass

    def create_from_message(message):
        idn = message.id.value
        position = message.pos_x.value, message.pos_y.value
        color = Color.from_int(message.color.value)
        return SharedTank(position, color, idn)
    def update_from_message(self, message):
        #self.body.position = message.pos_x.value, message.pos_y.value
        self.body.velocity = message.l_vel_x.value,  message.l_vel_y.value
        #self.body.angle = message.rot.value
        self.body.angular_velocity = message.a_vel.value
        self.barrelSprite.angular_velocity = message.turret_vel.value
        #self.alive = message.alive.value
         
    
    def get_message(self):
        message = TankUpdate()
        message.id.value = self.idn
        message.rot.value = self.body.angle
        message.pos_x.value = self.body.position[0]
        message.pos_y.value = self.body.position[1]
        message.l_vel_x.value = self.body.velocity[0]
        message.l_vel_y.value = self.body.velocity[1]
        message.a_vel.value = self.body.angular_velocity
        message.color.value = Color.to_int(self.color)
        message.turret_rot.value = self.barrelSprite.rotation
        message.turret_vel.value = self.barrelSprite.angular_velocity
        message.alive.value = self.alive
        return message


class SharedProjectile:
    SCALE = 0.65
    HEIGHT = 34 * SCALE
    WIDTH = 20 * SCALE
    class Ammo_Type(IntEnum):
        REGULAR = 1
        AP = 2
    def __init__(self, pos = (0,0), color=Color.RED, idn=0, src_idn = 0, type=Ammo_Type.REGULAR):
        self.idn = idn
        self.src_idn = src_idn
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
        #print("projectile at update server: ",self.body.angle, "id:", self.idn)
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
        return SharedProjectile(position, color, idn, src_id, projectile_type)

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
        return message


