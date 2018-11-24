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
from tile import Tile

tank = Tank(pos = (300,300), color = Color.RED)
tanks[tank.idn] = tank
tank2 = Tank(pos = (500,500), color = Color.BLACK, idn=1)
tanks[tank2.idn] = tank2
projectile_tank_handler = space.add_collision_handler(Coll_Type.TANK, Coll_Type.PROJECTILE)

def begin(arbiter, space, data):
    tankShape = arbiter.shapes[0]
    projectileShape = arbiter.shapes[1]
    tank = tanks[tankShape.idn]
    if projectiles.get(projectileShape.idn) is not None:
        projectile = projectiles[projectileShape.idn]
        if projectile.src_idn != tank.idn:
            print(projectile.src_idn)
            tank.hp -= Projectile.DAMAGE
            projectile.destroy()
            projectiles.pop(projectile.idn)
            print(tank.hp)
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
map1 = Game_Map.generate_map(26,26)
def reroll_map():
    global map1
    for x in range(len(map1.sprite_matrix)):
        map1.sprite_matrix[x].delete()
    map1 = Game_Map.generate_map(26,26)
@window.event
def on_draw():
    window.clear()
    bg_batch.draw()
    tank_batch.draw()
    barrel_batch.draw()
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
    if keys[key.SPACE]:
        reroll_map()
def update(dt):
    dtt = 1/60
    space.step(dtt)
    for tank in tanks.values():
        tank.update(dtt)
    for p in projectiles.values():
        p.update(dtt)
 
pyglet.clock.schedule_interval(update, 1.0/60)
pyglet.app.run()