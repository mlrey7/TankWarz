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
from global_vars import fg_batch
from global_vars import keys
from global_vars import projectiles
from global_vars import projectile_count
from global_vars import tank_group
from global_vars import barrel_group
from global_vars import smoke_group
from global_vars import explosion_group
from global_vars import effects
from global_vars import effect_count
from helper import Rectangle

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
        self.ammo_mode = Projectile.Ammo_Type.REGULAR
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
        self.hp_bar.update(self.sprite.position, self.hp)
        
        
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
        p.body.velocity = (1000*sin(self.barrelBody.angle),1000*cos(self.barrelBody.angle))
        p.body.angle = self.barrelBody.angle
        projectiles[p.idn] = p
        projectile_count+=1
        smoke_img = None
        if self.color == Color.BLACK or Color.BEIGE:
            smoke_img = pyglet.image.load("res/PNG/Smoke/smokeGrey4.png")
        elif self.color == Color.BLUE:
            smoke_img = pyglet.image.load("res/PNG/Smoke/smokeBlue4.png")
        elif self.color == Color.RED:
            smoke_img = pyglet.image.load("res/PNG/Smoke/smokeOrange4.png")
        else:
            smoke_img = pyglet.image.load("res/PNG/Smoke/smokeWhite4.png")
        smoke_img.anchor_x = smoke_img.width // 2
        smoke_img.anchor_y = (smoke_img.height // 2) + 35
        smoke_sprite = pyglet.sprite.Sprite(smoke_img, x = posx, y = posy, batch = fg_batch, group=smoke_group)
        smoke_sprite.scale = 0.6
        smoke_sprite.rotation = self.barrelSprite.rotation
        
        Tank.firing_sound.play()
        global effect_count
        effect_count += 1
        smoke_sprite.idn = effect_count
        effects[smoke_sprite.idn] = smoke_sprite
        def smoke(self):
            effects[smoke_sprite.idn].delete()
            effects.pop(smoke_sprite.idn)
        clock.schedule_once(smoke, 1)
        self.isReloading = True
        Tank.reloading_sound.play()
        def reload(self, idn):
            tanks[idn].isReloading = False
        clock.schedule_once(reload, 2, self.idn)
    def move(self, direction = Direction.FORWARD):
        if not self.moving:
            Tank.sound_player.play()
            self.sprite.image = self.anim
            self.moving = True
        self.body.velocity = (direction*Tank.SPEED*sin(self.body.angle),direction*Tank.SPEED*cos(self.body.angle))
    def stop(self):
        if self.moving:
            Tank.sound_player.pause()
            self.sprite.image = self.img
            self.moving = False
        self.body.velocity = (0,0)
    def rotate(self, direction = Direction.RIGHT):
        if not self.moving:
            Tank.sound_player.play()
        if not self.rotating:
            self.rotating = True
        self.body.angular_velocity = 1*direction
    def stopRotating(self):
        if not self.moving:
            Tank.sound_player.pause()
        if self.rotating:
            self.rotating = False
        self.body.angular_velocity = 0
    def rotateTurret(self, direction):
        self.barrelBody.angular_velocity = Tank.BARREL_SPEED*direction
    def stopRotateTurret(self):
        self.barrelBody.angular_velocity = 0
    def destroy(self):
        self.alive = False
        global effect_count
        effect_count += 1
        explosion_images = []
        for i in range(1,10):
            image = pyglet.image.load("res/PNG/Smoke/explosion/explosion%s.png" % (i))
            explosion_images.append(image)
        for i in range(len(explosion_images)):
            explosion_images[i].anchor_x = explosion_images[i].width // 2 
            explosion_images[i].anchor_y = explosion_images[i].height // 2 
        explosion_anim = pyglet.image.Animation.from_image_sequence(explosion_images, 0.16, False)
        explosion_sprite = pyglet.sprite.Sprite(explosion_anim, x = self.sprite.position[0], y = self.sprite.position[1] + 10, batch = fg_batch, group=explosion_group)
        explosion_sprite.scale = Tank.SCALE
        Tank.explosion_sound.play()
        effects[effect_count] = explosion_sprite
        