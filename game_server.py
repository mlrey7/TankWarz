import pyglet
import pymunk
import legume
import time
import threading

from pyglet.window import key
from pyglet import clock


from constants import Color
from constants import Coll_Type
from constants import Direction
from constants import Game

from game_map import Game_Map

import collision_handler
from shared import *
from server_global_vars import *

class Game_Server:
    def __init__(self, width, height, seed_a, seed_b):
        self.server = legume.Server()
        self.server.OnConnectRequest += self.join_request_handler
        self.server.OnMessage += self.message_handler
        self.update_timer = time.time()
        self.tanks = {}
        self.projectiles = {}
        self.seed_a = seed_a
        self.seed_b = seed_b
        
        collision_handler.Collision_Handler.initialize_handler(space, tanks, projectiles)

        create_walls()

        pyglet.clock.schedule_interval(self.update, 1.0/60)
        print("Server Initialized")

    def update(self, dt):
        dtt = 1.0/60.0
        space.step(dtt)
        for tank in self.tanks.values():
            tank.update(dtt)
        for p in projectiles.values():
            p.update(dtt)

    def message_handler(self, sender, message):
        if legume.messages.message_factory.is_a(message, 'TankCreate'):
            tanks[message.id.value] = Tank.create_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'TankUpdate'):
            tanks[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'TankCommand'):
            command = Tank.Command.from_int(message.command.value)
            tank = tanks[message.id.value]
            if command == Tank.Command.MOVE_FORWARD:
                tank.move(Direction.FORWARD)
            elif command == Tank.Command.MOVE_BACKWARD:
                tank.move(Direction.BACKWARD)
            elif command == Tank.Command.ROTATE_RIGHT:
                tank.rotate(Direction.RIGHT)
            elif command == Tank.Command.ROTATE_LEFT:
                tank.rotate(Direction.LEFT)
            elif command == Tank.Command.TURRET_ROTATE_RIGHT:
                tank.rotateTurret(Direction.RIGHT)
            elif command == Tank.Command.TURRET_ROTATE_LEFT:
                tank.rotateTurret(Direction.LEFT)
            elif command == Tank.Command.TURRET_ROTATE_RIGHT:
                tank.rotateTurret(Direction.RIGHT)
            elif command == Tank.Command.FIRE:
                tank.fire()
            elif command == Tank.Command.DESTROY:
                tank.destroy()
            else:
                print(command)

        elif legume.messages.message_factory.is_a(message, 'ProjectileCreate'):
            projectiles[message.id.value] = Projectile.create_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'ProjectileUpdate'):
            projectiles[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'MapCreate'):
            pass
        else:
            print('Message: %s' % message)

    def join_request_handler(self, sender, args):
        self.send_initial_state(sender)

    def _send_update(self):
        self.send_updates(self.server)

    def go(self):
        self.server.listen(('', PORT))
        print('Listening on port %d' % PORT)

        while True:
            # Physics stuff
            # self.update()

            # Network stuff
            if time.time() > self.update_timer + UPDATE_RATE:
                self._send_update()
                self.update_timer = time.time()
            self.server.update()
            time.sleep(0.0001)
    
    def send_updates(self, server):
        for tank in tanks.values():
            server.send_message_to_all(tank.get_message())
        for projectile in projectiles.values():
            server.send_message_to_all(projectile.get_message())

    def send_initial_state(self, endpoint):
        print("Connected to:", endpoint)
        # map_message = MapCreate()
        # map_message.l.value = number_tile_x
        # map_message.w.value = number_tile_y
        # map_message.seed_a = self.seed_a
        # map_message.seed_a = self.seed_b
        # endpoint.send_message(map_message)
        # for tank in tanks.values():
        #     endpoint.send_message(tank.get_message())
        # for projectile in projectiles.values():
        #     endpoint.send_message(projectile.get_message())

def create_walls():
    wall1_poly = pymunk.Poly.create_box(None, size=(10,full_height * 1.1))
    wall1_poly.collision_type = Coll_Type.ENVIRONMENT
    wall1_poly_moment = pymunk.moment_for_poly(250, wall1_poly.get_vertices())
    wall1_body = pymunk.Body(250, wall1_poly_moment, pymunk.Body.STATIC)
    wall1_poly.body = wall1_body
    wall1_body.position = 0,0
    space.add(wall1_poly, wall1_body) 

    wall2_poly = pymunk.Poly.create_box(None, size=(full_width * 2.3,10))
    wall2_poly.collision_type = Coll_Type.ENVIRONMENT
    wall2_poly_moment = pymunk.moment_for_poly(250, wall2_poly.get_vertices())
    wall2_body = pymunk.Body(250, wall2_poly_moment, pymunk.Body.STATIC)
    wall2_poly.body = wall2_body
    wall2_body.position = 0, full_height
    space.add(wall2_poly, wall2_body) 

    wall3_poly = pymunk.Poly.create_box(None, size=(10,full_height * 2.3))
    wall3_poly.collision_type = Coll_Type.ENVIRONMENT
    wall3_poly_moment = pymunk.moment_for_poly(250, wall3_poly.get_vertices())
    wall3_body = pymunk.Body(250, wall3_poly_moment, pymunk.Body.STATIC)
    wall3_poly.body = wall3_body
    wall3_body.position = full_width,0
    space.add(wall3_poly, wall3_body) 

    wall4_poly = pymunk.Poly.create_box(None, size=(full_width* 1.1,10))
    wall4_poly.collision_type = Coll_Type.ENVIRONMENT
    wall4_poly_moment = pymunk.moment_for_poly(250, wall4_poly.get_vertices())
    wall4_body = pymunk.Body(250, wall4_poly_moment, pymunk.Body.STATIC)
    wall4_poly.body = wall4_body
    wall4_body.position = 0,0
    space.add(wall4_poly, wall4_body) 

if __name__ == '__main__':
    server = Game_Server(Game.WIDTH, Game.HEIGHT, time.time(), time.time() + 2)
    net_thread = threading.Thread(target=server.go)
    net_thread.start()
    #game = pyglet.window.Window()
    pyglet.app.run()