import pyglet
import pymunk
import legume
import time
import threading
import operator
import logging

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
import server_global_vars
from sharedtank import SharedTank
from sharedprojectile import SharedProjectile
class Game_Server:
    def __init__(self, width, height, seed_a, seed_b):
        self.logger = logging.getLogger('Server')
        hdlr = logging.FileHandler('tankwarz_server.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.INFO)

        self.server = legume.Server()
        self.server.OnConnectRequest += self.join_request_handler
        self.server.OnMessage += self.message_handler
        self.update_timer = time.time()
        self.seed_a = seed_a
        self.seed_b = seed_b
        self.lock = threading.Lock()
        collision_handler.Server_Collision_Handler.initialize_handler(space, tanks, projectiles, self)
        self.game_clients_scores = {}
        create_walls()
        self.initial_time = 0
        self.time_running = False
        pyglet.clock.schedule_interval(self.update, 1.0/60)
        self.game_over = False
        self.logger.info('Server Initialized')

    def start_timer(self):
        self.initial_time = time.time()
        pyglet.clock.schedule_interval(self.update_time, 1.0)
        self.time_running = True
    def update_time(self, dt):
        elapsed_time = time.time() - self.initial_time
        rem_time = server_global_vars.game_length - elapsed_time
        if rem_time <= 0 and not self.game_over:
            msg = GameOver()
            sorted_d = sorted(self.game_clients_scores.items(), key=operator.itemgetter(1))
            msg.winner_id.value = sorted_d[-1][0]
            msg.score.value = sorted_d[-1][1]
            self.game_over = True
            self.server.send_reliable_message_to_all(msg)
        else:
            time_text = time.strftime("%M:%S", time.gmtime(rem_time))
            msg = UpdateTime()
            msg.time.value = time_text
            self.server.send_reliable_message_to_all(msg)
    def update(self, dt):
        dtt = 1.0/60.0
        space.step(dtt)
        for tank in tanks.values():
            tank.update(dtt)
        for p in projectiles.values():
            p.update(dtt)
        #self._send_update()
    def message_handler(self, sender, message):
        if legume.messages.message_factory.is_a(message, 'TankCreate'):
            self.logger.info("A server Tank has been created")
            if not self.time_running:
                self.start_timer()
            tanks[message.id.value] = SharedTank.create_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'TankUpdate'):
            tanks[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'TankCommand'):
            command = SharedTank.Command.from_int(message.command.value)
            tank = tanks[message.id.value]
            if command == SharedTank.Command.MOVE_FORWARD:
                tank.move(Direction.FORWARD)
            elif command == SharedTank.Command.MOVE_BACKWARD:
                tank.move(Direction.BACKWARD)
            elif command == SharedTank.Command.STOP_MOVING:
                tank.stop()
            elif command == SharedTank.Command.ROTATE_RIGHT:
                tank.rotate(Direction.RIGHT)
            elif command == SharedTank.Command.ROTATE_LEFT:
                tank.rotate(Direction.LEFT)
            elif command == SharedTank.Command.STOP_ROTATING:
                tank.stopRotating()
            elif command == SharedTank.Command.TURRET_ROTATE_RIGHT:
                tank.rotateTurret(Direction.RIGHT)
            elif command == SharedTank.Command.TURRET_ROTATE_LEFT:
                tank.rotateTurret(Direction.LEFT)
            elif command == SharedTank.Command.STOP_ROTATING_TURRET:
                tank.stopRotateTurret()
            elif command == SharedTank.Command.FIRE:
                tank.fire()
            elif command == SharedTank.Command.DESTROY:
                tank.destroy()  
            else:
                self.logger.info(command)
        elif legume.messages.message_factory.is_a(message, 'TankSwitchAmmo'):
            tank = tanks[message.id.value]
            tank.ammo_type = message.ammo_type.value
            self.server.send_message_to_all(message)
        elif legume.messages.message_factory.is_a(message, 'TankFire'):
            tank = tanks[message.id.value]
            tank.fire(message.projectile_id.value) 
            msg = TankFireClient()
            msg.id.value = message.id.value
            msg.projectile_id.value = message.projectile_id.value
            self.server.send_message_to_all(msg)
        elif legume.messages.message_factory.is_a(message, 'ProjectileCreate'):
            projectiles[message.id.value] = Projectile.create_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'ProjectileUpdate'):
            projectiles[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'MapCreate'):
            pass
        elif legume.messages.message_factory.is_a(message, 'ClientStart'):
            self.game_clients_scores.setdefault(message.client_id.value, 0)
        else:
            pass

    def join_request_handler(self, sender, args):
        self.send_initial_state(sender)

    def _send_update(self):
        self.send_updates(self.server)

    def go(self):
        self.server.listen(('', PORT))
        self.logger.info('Listening on port %d' % PORT)

        while True:
            if time.time() > self.update_timer + UPDATE_RATE:
                self._send_update()
                self.update_timer = time.time()
            self.server.update()
            time.sleep(0.0001)
    
    def send_updates(self, server):
        self.lock.acquire()
        try:
            for tank in tanks.values():
                server.send_message_to_all(tank.get_message())
            for projectile in projectiles.values():
                server.send_message_to_all(projectile.get_message())
        finally:
            self.lock.release()
            

    def send_initial_state(self, endpoint):
        self.logger.info("Connected to: %s" % endpoint)
        map_message = MapCreate()
        map_message.l.value = number_tile_x
        map_message.w.value = number_tile_y
        map_message.seed_a.value = int(self.seed_a)
        map_message.seed_b.value = int(self.seed_b)
        endpoint.send_message(map_message)
        self.lock.acquire()
        try:
            for tank in tanks.values():
                endpoint.send_message(tank.get_message())
            for projectile in projectiles.values():
                endpoint.send_message(projectile.get_message())
        finally:
            self.lock.release()

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
    pyglet.app.run()