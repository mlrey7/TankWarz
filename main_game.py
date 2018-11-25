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
from global_vars import hud_batch

from global_vars import keys
from global_vars import projectiles
from tank import Tank
from projectile import Projectile
from constants import Color
from constants import Coll_Type
from constants import Direction
from constants import Game
from game_map import Game_Map
from hud import Hud
from minimap import Minimap
from camera import Camera
import global_vars

def create_walls():
    wall1_poly = pymunk.Poly.create_box(None, size=(10,global_vars.full_height * 1.1))
    wall1_poly.collision_type = Coll_Type.ENVIRONMENT
    wall1_poly_moment = pymunk.moment_for_poly(250, wall1_poly.get_vertices())
    wall1_body = pymunk.Body(250, wall1_poly_moment, pymunk.Body.STATIC)
    wall1_poly.body = wall1_body
    wall1_body.position = 0,0
    space.add(wall1_poly, wall1_body) 

    wall2_poly = pymunk.Poly.create_box(None, size=(global_vars.full_width * 2.3,10))
    wall2_poly.collision_type = Coll_Type.ENVIRONMENT
    wall2_poly_moment = pymunk.moment_for_poly(250, wall2_poly.get_vertices())
    wall2_body = pymunk.Body(250, wall2_poly_moment, pymunk.Body.STATIC)
    wall2_poly.body = wall2_body
    wall2_body.position = 0, global_vars.full_height
    space.add(wall2_poly, wall2_body) 

    wall3_poly = pymunk.Poly.create_box(None, size=(10,global_vars.full_height * 2.3))
    wall3_poly.collision_type = Coll_Type.ENVIRONMENT
    wall3_poly_moment = pymunk.moment_for_poly(250, wall3_poly.get_vertices())
    wall3_body = pymunk.Body(250, wall3_poly_moment, pymunk.Body.STATIC)
    wall3_poly.body = wall3_body
    wall3_body.position = global_vars.full_width,0
    space.add(wall3_poly, wall3_body) 

    wall4_poly = pymunk.Poly.create_box(None, size=(global_vars.full_width* 1.1,10))
    wall4_poly.collision_type = Coll_Type.ENVIRONMENT
    wall4_poly_moment = pymunk.moment_for_poly(250, wall4_poly.get_vertices())
    wall4_body = pymunk.Body(250, wall4_poly_moment, pymunk.Body.STATIC)
    wall4_poly.body = wall4_body
    wall4_body.position = 0,0
    space.add(wall4_poly, wall4_body) 

tank = Tank(pos = (640,350), color = Color.RED)
tanks[tank.idn] = tank
tank2 = Tank(pos = (500,500), color = Color.BLACK, idn=1)
tanks[tank2.idn] = tank2

projectile_tank_handler = space.add_collision_handler(Coll_Type.TANK, Coll_Type.PROJECTILE)
projectile_environment_handler = space.add_collision_handler(Coll_Type.ENVIRONMENT, Coll_Type.PROJECTILE)

switch_sound = pyglet.media.load("res/sounds/switch28.wav", streaming=False)
bg_sound = pyglet.media.load("res/music/bgmusic2.wav", streaming=True)
bg_loop = pyglet.media.SourceGroup(bg_sound.audio_format, None)
bg_loop.loop = True
bg_loop.queue(bg_sound)
bg_player = pyglet.media.Player()
bg_player.queue(bg_loop)
bg_player.volume = 0.05

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
                tank.body.velocity = 0,0
                tank.body.angular_velocity = 0
                tank.destroy()
            else:
                tank.hit()
    return True
def pre_solve(arbiter, space, data):
    return True
def post_solve(arbiter, space, data):
    pass
def separate(arbiter, space, data):
    pass

def beginP(arbiter, space, data):
    projectileShape = arbiter.shapes[1]
    if projectiles.get(projectileShape.idn) is not None:
        projectile = projectiles[projectileShape.idn]
        projectile.destroy()
        projectiles.pop(projectile.idn)
        print("asdfasdf")
    return True

create_walls()

projectile_environment_handler.begin = beginP
projectile_tank_handler.begin = begin
projectile_tank_handler.pre_solve = pre_solve
projectile_tank_handler.post_solve = post_solve
projectile_tank_handler.separate = separate
map1 = Game_Map.generate_map(global_vars.number_tile_x,global_vars.number_tile_y)
minimap = Minimap(map1)
def reroll_map():
    global map1
    global minimap
    for x in range(len(map1.sprite_matrix)):
        map1.sprite_matrix[x].delete()
    map1 = Game_Map.generate_map(global_vars.number_tile_x,global_vars.number_tile_y)
    for x in range(len(minimap.sprite_matrix)):
        minimap.sprite_matrix[x].delete()
    minimap = Minimap(map1)
hud = Hud()
camera = Camera()
camera.init_gl(Game.WIDTH, Game.HEIGHT)
window.on_resize = camera.on_resize

@window.event
def on_draw():
    window.clear()
    camera.left = tank.sprite.position[0] - 640
    camera.right = camera.left + camera.width
    camera.bottom = tank.sprite.position[1] - 350
    camera.top = camera.bottom + camera.height
    if camera.left < 0:
        camera.left = 0
        camera.right = camera.left + Game.WIDTH
    elif camera.right > global_vars.full_width:
        camera.right = global_vars.full_width
        camera.left = camera.right - Game.WIDTH
    if camera.bottom < 0:
        camera.bottom = 0
        camera.top = Game.HEIGHT
    elif camera.top > global_vars.full_height:
        camera.top = global_vars.full_height
        camera.bottom = camera.top - Game.HEIGHT
    camera.apply_World()
    bg_batch.draw()
    fg_batch.draw()
    tank.hp_bar.draw()
    tank2.hp_bar.draw()
    camera.apply_Hud()
    hud.draw()
    hud_batch.draw()
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
    if keys[key.J]:
        tank.rotateTurret(Direction.LEFT)
    elif keys[key.L]:
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
    if keys[key.K] and not tank.isReloading:
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