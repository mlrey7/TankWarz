import pyglet
import pymunk
import legume
import time
import threading
from shared import *
from pyglet.window import key
from pyglet import clock

import global_vars
from global_vars import space
from global_vars import tanks
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
from global_vars import PORT
from global_vars import host

from game_map import Game_Map
from hud import Hud
from minimap import Minimap
from camera import Camera

import collision_handler
from pyglet.gl import Config

class Main_Window(pyglet.window.Window):
    
    def __init__(self, width, height, cl_id):
        conf = Config(sample_buffers=1,
                      samples=4,
                      depth_size=16,
                      double_buffer=True)
        super(Main_Window, self).__init__(Game.WIDTH, Game.HEIGHT, config=conf)
        self.running = False
        self.cl_id = cl_id
        self.tank = None
        self.switch_sound = pyglet.media.load("res/sounds/switch28.wav", streaming=False)
        self.bg_sound = pyglet.media.load("res/music/bgmusic2.wav", streaming=True)
        self.bg_loop = pyglet.media.SourceGroup(self.bg_sound.audio_format, None)
        self.bg_loop.loop = True
        self.bg_loop.queue(self.bg_sound)
        self.bg_player = pyglet.media.Player()
        self.bg_player.volume = 0.05
        self.bg_player.queue(self.bg_loop)
        self.game_map = None
        self.minimap = None

        self.hud = None
        self.camera = None

    def start_game(self):
        self.push_handlers(keys)

        self.tank = tanks[self.cl_id]

        collision_handler.Collision_Handler.initialize_handler(space, tanks, projectiles)

        create_walls()

        self.hud = Hud()
        self.camera = Camera()
        self.camera.init_gl(Game.WIDTH, Game.HEIGHT)
        self.on_resize = self.camera.on_resize

        self.bg_player.play()

        pyglet.clock.schedule_interval(self.update, 1.0/60)
        self.running = True

    def update_camera_player(self):
        self.camera.left = self.tank.sprite.position[0] - 640
        self.camera.right = self.camera.left + self.camera.width
        self.camera.bottom = self.tank.sprite.position[1] - 350
        self.camera.top = self.camera.bottom + self.camera.height
        if self.camera.left < 0:
            self.camera.left = 0
            self.camera.right = self.camera.left + Game.WIDTH
        elif self.camera.right > global_vars.full_width:
            self.camera.right = global_vars.full_width
            self.camera.left = self.camera.right - Game.WIDTH
        if self.camera.bottom < 0:
            self.camera.bottom = 0
            self.camera.top = Game.HEIGHT
        elif self.camera.top > global_vars.full_height:
            self.camera.top = global_vars.full_height
            self.camera.bottom = self.camera.top - Game.HEIGHT

    def on_draw(self):
        self.clear()
        if self.running:
            self.update_camera_player()
            self.camera.apply_World()
            bg_batch.draw()
            fg_batch.draw()
            for t in tanks.values():
                t.hp_bar.draw()
            self.camera.apply_Hud()
            self.hud.draw()
            hud_batch.draw()
            self.minimap.update()

        if keys[key._1]:
            if self.tank.ammo_mode == Projectile.Ammo_Type.AP:
                self.switch_sound.play()
                self.tank.ammo_mode = Projectile.Ammo_Type.REGULAR

                self.hud.bullet1_overlay.color = (40,40,40,200)
                self.hud.bullet1_sprite.opacity = 255
                self.hud.bullet1_text.color = (255,255,255,255)
                self.hud.bullet1_ammo.color = (255,255,255,255)

                self.hud.bullet2_overlay.color = (40,40,40,100)
                self.hud.bullet2_sprite.opacity = 100
                self.hud.bullet2_text.color = (255,255,255,100)
                self.hud.bullet2_ammo.color = (255,255,255,100)
        elif keys[key._2]:
            if self.tank.ammo_mode == Projectile.Ammo_Type.REGULAR:
                self.switch_sound.play()
                self.tank.ammo_mode = Projectile.Ammo_Type.AP
                self.hud.bullet1_overlay.color = (40,40,40,100)
                self.hud.bullet1_sprite.opacity = 100
                self.hud.bullet1_text.color = (255,255,255,100)
                self.hud.bullet1_ammo.color = (255,255,255,100)

                self.hud.bullet2_overlay.color = (40,40,40,200)
                self.hud.bullet2_sprite.opacity = 255
                self.hud.bullet2_text.color = (255,255,255,255)
                self.hud.bullet2_ammo.color = (255,255,255,255)

        if keys[key.J]:
            msg = TankCommand()
            msg.id.value = self.cl_id
            msg.command.value = Tank.Command.ROTATE_LEFT
            self._client.send_message(msg)
            self.tank.rotateTurret(Direction.LEFT)
        elif keys[key.L]:
            self.tank.rotateTurret(Direction.RIGHT)
        else:
            self.tank.stopRotateTurret()
        if keys[key.W]:
            self.tank.move(Direction.FORWARD)
        elif keys[key.S]:
            self.tank.move(Direction.BACKWARD)
        else:
            self.tank.stop()
        if keys[key.D]:
            self.tank.rotate(Direction.RIGHT)
        elif keys[key.A]:
            self.tank.rotate(Direction.LEFT)
        else:
            self.tank.stopRotating()
        if keys[key.K] and not self.tank.isReloading:
            self.tank.fire()
            self.hud.update(self.tank.ammo1, self.tank.ammo2)
        # if keys[key.SPACE]:
        #     pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')
        #     self.reroll_map()

    def update(self, dt):
        dtt = 1.0/60.0
        space.step(dtt)
        for tank in tanks.values():
            tank.update(dtt)
        for p in projectiles.values():
            p.update(dtt)

    # def on_connect_accepted(self, sender, args):
    #     print("CONNECTED")
    # def on_connect_rejected(self, sender, args):
    #     print("NOT CONNECTED")
    def message_handler(self, sender, message):
        if legume.messages.message_factory.is_a(message, 'TankCreate'):
            if tanks.get(message.id.value) is None:
                tanks[message.id.value] = Tank.create_from_message(message)
                if message.id.value == self.cl_id:
                    self.start_game()
            else:
                tanks[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'TankUpdate'):
            if tanks.get(message.id.value) is None:
                tanks[message.id.value] = Tank.create_from_message(message)
            else:
                tanks[message.id.value].update_from_message(message)
        if self.running:
            if legume.messages.message_factory.is_a(message, 'TankCommand'):
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
                l = message.l.value
                w = message.w.value
                seed_a = int(message.seed_a.value)
                seed_b = int(message.seed_b.value)
                self.game_map = Game_Map.generate_map(l,w, seed_a, seed_b)
                self.minimap = Minimap(self.game_map)
            else:
                print('Message: %s' % message)

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

class Game_Client:

    def __init__(self):
        self.cl_id = int(time.time())
        self.running = True
        self._client = legume.Client()
        #self._client.OnMessage += self.message_handler
        #self._client.OnConnectRequestAccepted += self.on_connect_accepted
        # self._client.OnConnectRequestRejected += self.on_connect_rejected
        self.lock = threading.Lock()
    def on_connect_accepted(self, sender, args):
        print("CONNECTED")
    def on_connect_rejected(self, sender, args):
        print("NOT CONNECTED")
    def connect(self, host='localhost'):
        self._client.connect((host, PORT))
    def go(self):
        while self.running:
            try:
                self.lock.acquire()
                self._client.update()
            except:
                self.running = False
                raise
            finally:
                pass
                self.lock.release()
            time.sleep(0.0001)
        print('Exited go')


if __name__ == '__main__':
    game = None
    game_client = Game_Client()
    def on_connect_accepted(self,args):
        print("Connected")
        message = TankCreate()
        message.id.value = game_client.cl_id
        message.pos_x.value = 500
        message.pos_y.value = 500
        message.rot.value = 0
        message.l_vel_x.value = 0
        message.l_vel_y.value = 0
        message.a_vel.value = 0
        message.color.value = 1
        game_client._client.send_message(message)
        game = Main_Window(Game.WIDTH, Game.HEIGHT, game_client.cl_id) 
        game_client._client.OnMessage += game.message_handler
    def on_connect_rejected(self,  args):
        print("Error connecting") 
    game_client._client.OnConnectRequestAccepted += on_connect_accepted
    game_client._client.OnConnectRequestRejected += on_connect_rejected
    game_client.connect(host)

    net_thread = threading.Thread(target=game_client.go)
    net_thread.start()
    pyglet.app.run()






