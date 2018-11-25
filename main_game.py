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
from global_vars import tank_batch
from global_vars import barrel_batch
from global_vars import keys
from global_vars import projectiles
from tank import Tank
from projectile import Projectile
from constants import Color
from constants import Coll_Type
from constants import Direction
from game_map import Game_Map
from hud import Hud
from minimap import Minimap

tank = Tank(pos = (300,300), color = Color.RED)
tanks[tank.idn] = tank
tank2 = Tank(pos = (500,500), color = Color.BLACK, idn=1)
tanks[tank2.idn] = tank2
projectile_tank_handler = space.add_collision_handler(Coll_Type.TANK, Coll_Type.PROJECTILE)
switch_sound = pyglet.media.load("res/sounds/switch28.wav", streaming=False)
bg_sound = pyglet.media.load("res/music/bgmusic2.wav", streaming=True)
bg_loop = pyglet.media.SourceGroup(bg_sound.audio_format, None)
bg_loop.loop = True
bg_loop.queue(bg_sound)
bg_player = pyglet.media.Player()
bg_player.queue(bg_loop)
bg_player.volume = 0.05

pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

def begin(arbiter, space, data):
    tankShape = arbiter.shapes[0]
    projectileShape = arbiter.shapes[1]
    tank = tanks[tankShape.idn]
    if projectiles.get(projectileShape.idn) is not None:
        projectile = projectiles[projectileShape.idn]
        if projectile.src_idn != tank.idn:
            print(projectile.src_idn)
            tank.hp -= projectile.damage
            projectile.destroy()
            projectiles.pop(projectile.idn)
            if tank.hp <= 0 and tank.alive:
                tank.destroy()
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
map1 = Game_Map.generate_map(30,30)
minimap = Minimap(map1)
def reroll_map():
    global map1
    global minimap
    for x in range(len(map1.sprite_matrix)):
        map1.sprite_matrix[x].delete()
    map1 = Game_Map.generate_map(30,30)
    for x in range(len(minimap.sprite_matrix)):
        minimap.sprite_matrix[x].delete()
    minimap = Minimap(map1)
hud = Hud()
@window.event
def on_draw():
    window.clear()
    bg_batch.draw()
    hud.draw()
    fg_batch.draw()
    tank.hp_bar.draw()
    tank2.hp_bar.draw()
    minimap.update()
    if keys[key._1]:
        if tank.ammo_mode == Projectile.Ammo_Type.AP:
            switch_sound.play()
            tank.ammo_mode = Projectile.Ammo_Type.REGULAR

            hud.bullet1_overlay.color = (40,40,40,200)
            hud.bullet1_sprite.opacity = 255
            hud.bullet1_text.color = (255,255,255,255)
            hud.bullet1_ammo.color = (255,255,255,255)

            hud.bullet2_overlay.color = (40,40,40,100)
            hud.bullet2_sprite.opacity = 100
            hud.bullet2_text.color = (255,255,255,100)
            hud.bullet2_ammo.color = (255,255,255,100)
    elif keys[key._2]:
        if tank.ammo_mode == Projectile.Ammo_Type.REGULAR:
            switch_sound.play()
            tank.ammo_mode = Projectile.Ammo_Type.AP
            hud.bullet1_overlay.color = (40,40,40,100)
            hud.bullet1_sprite.opacity = 100
            hud.bullet1_text.color = (255,255,255,100)
            hud.bullet1_ammo.color = (255,255,255,100)

            hud.bullet2_overlay.color = (40,40,40,200)
            hud.bullet2_sprite.opacity = 255
            hud.bullet2_text.color = (255,255,255,255)
            hud.bullet2_ammo.color = (255,255,255,255)
    if keys[key.Q]:
        tank.rotateTurret(Direction.LEFT)
    elif keys[key.E]:
        tank.rotateTurret(Direction.RIGHT)
    else:
        tank.stopRotateTurret()
    if keys[key.W]:
        tank.move(Direction.FORWARD)
    elif keys[key.S]:
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
        hud.update(tank.ammo1, tank.ammo2)
    if keys[key.SPACE]:
        pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')
        reroll_map()
def update(dt):
    dtt = 1/60
    space.step(dtt)
    for tank in tanks.values():
        tank.update(dtt)
    for p in projectiles.values():
        p.update(dtt)
bg_player.play()

pyglet.clock.schedule_interval(update, 1.0/60)
pyglet.app.run()