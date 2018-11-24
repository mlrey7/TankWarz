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
from global_vars import space
from global_vars import tanks
from global_vars import window
from global_vars import bg_batch
from global_vars import fg_batch
from global_vars import hud_group
from global_vars import tank_batch
from global_vars import barrel_batch
from global_vars import keys
from global_vars import projectiles
from tank import Tank
from projectile import Projectile
from constants import Color
from constants import Game
from constants import Coll_Type
from constants import Direction
from game_map import Game_Map
from helper import Rectangle
class Hud:
    def __init__(self):
        self.bullet1_x = Game.WIDTH - 100
        self.bullet1_y = 200

        self.bullet2_x = Game.WIDTH - 100
        self.bullet2_y = 165

        self.bullet1_overlay = Rectangle(self.bullet1_x, self.bullet1_y, 100, 35, (40,40,40,200))
        self.bullet1_img = pyglet.image.load("res/PNG/bullets/bulletBeige_outline.png")
        self.bullet1_img.anchor_x = self.bullet1_img.width // 2 
        self.bullet1_img.anchor_y = self.bullet1_img.height // 2 
        self.bullet1_sprite = pyglet.sprite.Sprite(self.bullet1_img, x = self.bullet1_x + 20, y = self.bullet1_y + self.bullet1_overlay.height // 2, batch = fg_batch, group=hud_group)
        self.bullet1_sprite.scale = 0.75
        self.bullet1_ammo = pyglet.text.HTMLLabel(
        '<font face="Arial" size="13" color="white"><b>x40</b></font>',
        x=self.bullet1_x+45, y=self.bullet1_y + self.bullet1_overlay.height // 2,
        anchor_x='center', anchor_y='center')
        self.bullet1_text = pyglet.text.HTMLLabel(
        '<font face="Arial" size="13" color="white"><b>1</b></font>',
        x=self.bullet1_x+80, y=self.bullet1_y + self.bullet1_overlay.height // 2,
        anchor_x='center', anchor_y='center')

        self.bullet2_overlay = Rectangle(self.bullet2_x, self.bullet2_y, 100, 35, (40,40,40,100))
        self.bullet2_img = pyglet.image.load("res/PNG/bullets/bulletBeigeSilver_outline.png")
        self.bullet2_img.anchor_x = self.bullet1_img.width // 2 
        self.bullet2_img.anchor_y = self.bullet1_img.height // 2 
        self.bullet2_sprite = pyglet.sprite.Sprite(self.bullet2_img, x = self.bullet2_x + 20, y = self.bullet2_y + self.bullet2_overlay.height // 2, batch = fg_batch, group=hud_group)
        self.bullet2_sprite.scale = 0.75
        self.bullet2_sprite.opacity = 100
        self.bullet2_ammo = pyglet.text.HTMLLabel(
        '<font face="Arial" size="13" color="white"><b>x5</b></font>',
        x=self.bullet2_x+45, y=self.bullet2_y + self.bullet2_overlay.height // 2,
        anchor_x='center', anchor_y='center')
        self.bullet2_text = pyglet.text.HTMLLabel(
        '<font face="Arial" size="13" color="white"><b>2</b></font>',
        x=self.bullet2_x+80, y=self.bullet2_y + self.bullet2_overlay.height // 2,
        anchor_x='center', anchor_y='center')

        self.bullet2_text.color = (255,255,255,100)
        self.bullet2_ammo.color = (255,255,255,100)
    def update(self, ammo1, ammo2):
        self.bullet1_ammo = pyglet.text.HTMLLabel(
        '<font face="Arial" size="13" color="white"><b>x%d</b></font>' % (ammo1),
        x=self.bullet1_x+45, y=self.bullet1_y + self.bullet1_overlay.height // 2,
        anchor_x='center', anchor_y='center')
        self.bullet2_ammo = pyglet.text.HTMLLabel(
        '<font face="Arial" size="13" color="white"><b>x%d</b></font>' % (ammo2),
        x=self.bullet2_x+45, y=self.bullet2_y + self.bullet2_overlay.height // 2,
        anchor_x='center', anchor_y='center')
    def draw(self):
        self.bullet1_overlay.draw()
        self.bullet1_text.draw()
        self.bullet1_ammo.draw()

        self.bullet2_overlay.draw()
        self.bullet2_text.draw()
        self.bullet2_ammo.draw()