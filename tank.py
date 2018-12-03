import pyglet
import pymunk
from pyglet import clock
import math
from math import degrees
from math import sin
from math import cos
from math import radians
import constants

from projectile import Projectile
from constants import Color
from constants import Coll_Type
from constants import Direction

from global_vars import space
from global_vars import tanks
from global_vars import fg_batch

from global_vars import projectiles
from global_vars import projectile_count
from global_vars import tank_group
from global_vars import barrel_group
from global_vars import smoke_group
from global_vars import explosion_group
from global_vars import effects
from global_vars import effect_count

from helper import Rectangle
from enum import IntEnum
import shared


class Tank:
    SCALE = 0.65
    HEIGHT = 78 * math.sqrt(SCALE)
    WIDTH = 83 * math.sqrt(SCALE)
    BARREL_HEIGHT = 58
    BARREL_WIDTH = 24
    BARREL_SPEED = 1
    firing_sound = pyglet.media.load("res/sounds/tank_fire.wav", streaming=False)
    moving_sound = pyglet.media.load("res/sounds/tank_moving.wav", streaming=False)
    reloading_sound = pyglet.media.load("res/sounds/tank_reload.wav", streaming=False)
    explosion_sound = pyglet.media.load("res/sounds/tank_explosion.wav", streaming=False)
    moving_sound_loop = pyglet.media.SourceGroup(moving_sound.audio_format, None)
    moving_sound_loop.loop = True
    moving_sound_loop.queue(moving_sound)
    sound_player = pyglet.media.Player()
    sound_player.queue(moving_sound_loop)
    sound_player.volume = 0.05
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
            return Tank.CommandInt[c]

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

    class HP_Bar:
        def __init__(self, pos):
            self.border = Rectangle(pos[0] - (54 / 2) - 3,pos[1]+51, 60, 16, (40,40,40,255))
            self.full_bar = Rectangle(pos[0] - (54 / 2),pos[1]+50, 54, 10, (255,0,0,255))
            self.hp_bar = Rectangle(pos[0] - (54 / 2),pos[1]+50, 54, 10, (0,255,0,255))
        def update(self, position, hp):
            self.full_bar.lx = position[0] - (54 / 2)
            self.full_bar.ly = position[1] + 50
            self.hp_bar.lx = position[0] - (54 / 2)
            self.hp_bar.ly = position[1] + 50
            self.border.lx = self.hp_bar.lx - 3
            self.border.ly = self.hp_bar.ly - 3
            self.hp_bar.width = max(54 - (.54 * (100 - hp)), 0)
        def draw(self):
            self.border.draw()
            self.full_bar.draw()
            self.hp_bar.draw()

    def __init__(self, pos = (0, 0), color=Color.RED, idn=0):
        self.alive = True
        self.destroyed = False
        self.hp = 100
        self.ammo1 = 40
        self.ammo2 = 5
        self.isReloading = False
        self.sprite = None
        self.barrelSprite = None
        self.color = color
        self.rotating = False
        self.moving = False
        self.idn = idn
        self.ammo_type = Projectile.Ammo_Type.REGULAR
        self.hp_bar = Tank.HP_Bar(pos)
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
        self.sprite = pyglet.sprite.Sprite(self.img, x = pos[0], y = pos[1], batch = fg_batch, group=tank_group)
        self.sprite.scale = Tank.SCALE

        barrelImg = pyglet.image.load("res/PNG/tanks/barrel%s_outline.png" % color.value)
        barrelImg.anchor_x = barrelImg.width // 2 
        barrelImg.anchor_y = (barrelImg.height // 2) - 15
        self.barrelSprite = pyglet.sprite.Sprite(barrelImg, x = pos[0], y = pos[1], batch = fg_batch, group=barrel_group)
        self.barrelSprite.scale = Tank.SCALE 
        self.barrelSprite.angular_velocity = 0
        self.poly = pymunk.Poly.create_box(None, size=(Tank.HEIGHT,Tank.WIDTH), radius=0.1)
        self.poly.collision_type = Coll_Type.TANK
        self.poly.idn = self.idn
        self.moment = pymunk.moment_for_poly(50000, self.poly.get_vertices())
        self.body = pymunk.Body(50000, self.moment, pymunk.Body.DYNAMIC)
        self.poly.body = self.body
        self.body.position = pos

        self.destroyed_img = pyglet.image.load("res/PNG/tanks/Destroyed/%s.png" % color.value)
        self.destroyed_img.anchor_x = self.destroyed_img.width // 2 
        self.destroyed_img.anchor_y = self.destroyed_img.height // 2 
        self.burning_sprite = None
        
        # points = [(0,0),(0,58),(24,58),(24,0)]
        # #self.barrelPoly = pymunk.Poly(None, points, transform=(0,0))
        # self.barrelPoly = pymunk.Poly.create_box(None, size=(58,24), radius=0.1)
        # self.barrelMoment = pymunk.moment_for_poly(10.0, self.barrelPoly.get_vertices(), offset=(0,-10))
        # self.barrelBody = pymunk.Body(10.0, self.barrelMoment, pymunk.Body.DYNAMIC)
        # self.barrelPoly.sensor = True
        # self.barrelPoly.body = self.barrelBody
        # self.barrelBody.position = pos
        # print("starting barrel pos", self.barrelBody.position)
        # joint = pymunk.constraint.PinJoint(self.body, self.barrelBody)
        # joint.collide_bodies = False
        space.add(self.poly, self.body)
        #space.add(self.barrelPoly, self.barrelBody)


    def update(self, dt):
        self.sprite.position = self.body.position
        self.sprite.rotation = degrees(self.body.angle)
        # self.barrelBody.velocity = 0,0
        # self.barrelBody.position = self.body.position[0], self.body.position[1]
        # # self.barrelBody.velocity = 0,0
        # print(self.barrelBody)
        # print(self.barrelBody.position)
        # print(self.barrelSprite.rotation)
        # print(degrees(self.barrelSprite.angular_velocity) * dt)
        self.barrelSprite.rotation += degrees(self.barrelSprite.angular_velocity) * dt
        self.barrelSprite.position = self.body.position
        
        #self.barrelSprite.rotation = degrees(self.barrelBody.angle)
        self.hp_bar.update(self.sprite.position, self.hp)
        if not self.alive and not self.destroyed:
            burning_images = []
            for i in range(1,5):
                image = pyglet.image.load("res/PNG/Tanks/Flame/Loop/%s.png" % (i))
                burning_images.append(image)
            for i in range(len(burning_images)):
                burning_images[i].anchor_x = burning_images[i].width // 2 
                burning_images[i].anchor_y = burning_images[i].height // 2 
            burning_anim = pyglet.image.Animation.from_image_sequence(burning_images, 0.16, True)
            self.burning_sprite = pyglet.sprite.Sprite(burning_anim, x = self.sprite.position[0], y = self.sprite.position[1], batch = fg_batch, group=explosion_group)
            self.burning_sprite.scale = Tank.SCALE
            self.sprite.image = self.destroyed_img
            self.destroyed = True
            
        
    def fire(self, projectile_id):
        print("fireeee")
        if self.ammo_type == Projectile.Ammo_Type.REGULAR and self.ammo1 <= 0 or self.ammo_type == Projectile.Ammo_Type.AP and self.ammo2 <= 0:
            return
        if self.ammo_type == Projectile.Ammo_Type.REGULAR:
            self.ammo1 -= 1
        elif self.ammo_type == Projectile.Ammo_Type.AP:
            self.ammo2 -= 1
        posx = self.body.position[0] + (sin(radians(self.barrelSprite.rotation)) * 50)
        posy = self.body.position[1] + (cos(radians(self.barrelSprite.rotation)) * 50)
        global projectile_count
        p = Projectile(pos=(posx, posy), color=self.color, idn=projectile_id,src_idn=self.idn, type=self.ammo_type)
        p.body.velocity = (p.velocity*sin(radians(self.barrelSprite.rotation)),p.velocity*cos(radians(self.barrelSprite.rotation)))
        #print(self.barrelSprite.rotation)
        p.body.angle = radians(self.barrelSprite.rotation)
        #print("projectile at start client: ",p.body.angle, "id:", p.idn)
        projectiles[p.idn] = p
        projectile_count+=1
        smoke_img = None

        smoke_images = []
        for i in range(1,8):
            image = pyglet.image.load("res/PNG/Tanks/Fire/%d.png" % (i))
            smoke_images.append(image)
        for i in range(len(smoke_images)):
            smoke_images[i].anchor_x = smoke_images[i].width // 2 + 5
            smoke_images[i].anchor_y = (smoke_images[i].height // 2) - 80
        smoke_anim = pyglet.image.Animation.from_image_sequence(smoke_images, 0.1, False)
        smoke_sprite = pyglet.sprite.Sprite(smoke_anim, x = self.sprite.position[0], y = self.sprite.position[1], batch = fg_batch, group=smoke_group)
        smoke_sprite.scale = Tank.SCALE
        smoke_sprite.rotation = self.barrelSprite.rotation
        
        # Tank.firing_sound.play()
        # Tank.reloading_sound.play()
        self.isReloading = True

        global effect_count
        effect_count += 1
        smoke_sprite.idn = effect_count
        effects[smoke_sprite.idn] = smoke_sprite
        def smoke(self):
            effects[smoke_sprite.idn].delete()
            effects.pop(smoke_sprite.idn)
        clock.schedule_once(smoke, 1)

        def reload(self, idn):
            print("tapos na reload")
            tanks[idn].isReloading = False
        clock.schedule_once(reload, 2, self.idn)
        
    def move(self, direction = Direction.FORWARD):
        if not self.moving and self.alive:
            Tank.sound_player.play()
            self.sprite.image = self.anim
            self.moving = True
        if self.alive:
            self.body.velocity = (direction*Tank.SPEED*sin(self.body.angle),direction*Tank.SPEED*cos(self.body.angle))
        #print("client v,angle", self.body.velocity, degrees(self.body.angle))
    def stop(self):
        if self.moving and self.alive:
            Tank.sound_player.pause()
            self.sprite.image = self.img
            self.moving = False
            self.body.velocity = (0,0)
    def rotate(self, direction = Direction.RIGHT):
        if not self.moving and self.alive:
            Tank.sound_player.play()
        if not self.rotating:
            self.rotating = True
        if self.alive:    
            self.body.angular_velocity = 1*direction
    def stopRotating(self):
        if not self.moving:
            Tank.sound_player.pause()
        if self.rotating:
            self.rotating = False
            self.body.angular_velocity = 0
    def rotateTurret(self, direction):
        if self.alive:
        #self.barrelBody.angular_velocity = Tank.BARREL_SPEED*direction
            self.barrelSprite.angular_velocity = Tank.BARREL_SPEED*direction
    def stopRotateTurret(self):
        #self.barrelBody.angular_velocity = 0
        self.barrelSprite.angular_velocity = 0
    def destroy(self):
        #print("DEADBALLZ")
        self.alive = False
        #print("destroyed")
        explosion_images = []
        for i in range(1,11):
            image = pyglet.image.load("res/PNG/Tanks/Flame/Explode/%s.png" % (i))
            explosion_images.append(image)
        for i in range(len(explosion_images)):
            explosion_images[i].anchor_x = explosion_images[i].width // 2 
            explosion_images[i].anchor_y = explosion_images[i].height // 2 
        explosion_anim = pyglet.image.Animation.from_image_sequence(explosion_images, 0.16, False)
        explosion_sprite = pyglet.sprite.Sprite(explosion_anim, x = self.sprite.position[0], y = self.sprite.position[1] + 10, batch = fg_batch, group=explosion_group)
        explosion_sprite.scale = Tank.SCALE
        Tank.explosion_sound.play()

        global effect_count
        effect_count += 1
        explosion_sprite.idn = effect_count
        effects[effect_count] = explosion_sprite

        # burning_images = []
        # for i in range(1,5):
        #     image = pyglet.image.load("res/PNG/Tanks/Flame/Loop/%s.png" % (i))
        #     burning_images.append(image)
        # for i in range(len(burning_images)):
        #     burning_images[i].anchor_x = burning_images[i].width // 2 
        #     burning_images[i].anchor_y = burning_images[i].height // 2 
        # burning_anim = pyglet.image.Animation.from_image_sequence(burning_images, 0.16, True)
        
        # self.burning_sprite = pyglet.sprite.Sprite(burning_anim, x = self.sprite.position[0], y = self.sprite.position[1], batch = fg_batch, group=explosion_group)
        # self.burning_sprite.scale = Tank.SCALE
        # self.sprite.image = self.destroyed_img
        def explosion_s(self):
            effects[explosion_sprite.idn].delete()
            effects.pop(explosion_sprite.idn)
            
        clock.schedule_once(explosion_s, 1)

    def hit(self, damage):
        self.hp -= damage
        if self.hp <= 0 and self.alive:
            self.body.velocity = 0,0
            self.body.angular_velocity = 0
            self.destroy()
        else:
            hit_images = []
            for i in range(1,10):
                image = pyglet.image.load("res/PNG/Tanks/hit/%d.png" % (i))
                hit_images.append(image)
            for i in range(len(hit_images)):
                hit_images[i].anchor_x = hit_images[i].width // 2 
                hit_images[i].anchor_y = hit_images[i].height // 2 + 5
            hit_anim = pyglet.image.Animation.from_image_sequence(hit_images, 0.1, False)
            hit_sprite = pyglet.sprite.Sprite(hit_anim, x = self.sprite.position[0], y = self.sprite.position[1], batch = fg_batch, group=explosion_group)
            hit_sprite.scale = Tank.SCALE
            hit_sprite.rotation = self.sprite.rotation

            global effect_count
            effect_count += 1
            hit_sprite.idn = effect_count
            effects[effect_count] = hit_sprite

            def hit_s(self):
                effects[hit_sprite.idn].delete()
                effects.pop(hit_sprite.idn)
            clock.schedule_once(hit_s, 1)

    def create_from_message(message):
        idn = message.id.value
        position = message.pos_x.value, message.pos_y.value
        color = Color.from_int(message.color.value)
        return Tank(position, color, idn)
    def update_from_message(self, message):
        #print("client tank v,angle", self.body.velocity, degrees(self.body.angle))
        self.body.position = message.pos_x.value, message.pos_y.value
        self.body.velocity = message.l_vel_x.value,  message.l_vel_y.value
        self.body.angle = message.rot.value
        self.body.angular_velocity = message.a_vel.value
        self.barrelSprite.position = self.body.position
        self.barrelSprite.rotation = message.turret_rot.value
        self.barrelSprite.angular_velocity = message.turret_vel.value
        self.alive = message.alive.value
        self.update(1.0/60)
    def get_message_all(self):
        message = shared.TankCreate()
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
        #print("client tank after v,angle", self.body.velocity, degrees(self.body.angle))
    def get_message(self):
        message = shared.TankUpdate()
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