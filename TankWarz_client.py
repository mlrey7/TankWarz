import pyglet
import pymunk
import legume
import time
import glooey
import random
import logging
from shared import *
from pyglet.window import key
from pyglet import clock
import sys
import global_vars
from global_vars import space
from global_vars import tanks
from global_vars import bg_batch
from global_vars import fg_batch
from global_vars import hud_batch
from global_vars import gui_batch
from global_vars import keys
from global_vars import projectiles
from global_vars import host
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

pyglet.font.add_file("res/fonts/camouflagew.ttf")
class TitleLabel(glooey.Label):
    custom_font_name = 'Camouflage Woodland'
    custom_font_size = 60
    custom_color = '#ffffff'
    custom_alignment = 'center'
class SubtitleLabel(glooey.Label):
    custom_font_name = 'Camouflage Woodland'
    custom_font_size = 30
    custom_color = '#ffffff'
    custom_alignment = 'center'
class TitleScreen_Grid(glooey.VBox):
    custom_alignment = 'fill'
class TitleScreen_Button(glooey.Button):
    class Label(glooey.Label):
        custom_font_name = 'Camouflage Woodland'
        custom_font_size = 25
        custom_color = '#ffffff'
        custom_alignment = 'center'
        custom_vert_padding = 10
        custom_horz_padding = 15
    class Base(glooey.Background):
        custom_color = '#a2a2a2'
    class Over(glooey.Background):
        custom_color = '#737373'
    class Down(glooey.Background):
        custom_color = '#737373'
class Start_Button(TitleScreen_Button): 
    def __init__(self, client):
        super().__init__("")
        self.client = client
    def on_click(self, widget):
        self.client.connect(host)
    class Base(glooey.Image):
        custom_image = pyglet.resource.image('res/PNG/GUI/pl_up2.png')
    class Over(glooey.Background):
        custom_image = pyglet.resource.image('res/PNG/GUI/pl_down2.png')
    class Down(glooey.Background):
        custom_image = pyglet.resource.image('res/PNG/GUI/pl_down2.png')
class Exit_Button(TitleScreen_Button):
    def on_click(self, widget):
        sys.exit()
    class Base(glooey.Image):
        custom_image = pyglet.resource.image('res/PNG/GUI/ex_up2.png')
    class Over(glooey.Background):
        custom_image = pyglet.resource.image('res/PNG/GUI/ex_down2.png')
    class Down(glooey.Background):
        custom_image = pyglet.resource.image('res/PNG/GUI/ex_down2.png')
class PlayAgain_Button(TitleScreen_Button):
    class Base(glooey.Image):
        custom_image = pyglet.resource.image('res/PNG/GUI/pa_up2.png')
    class Over(glooey.Background):
        custom_image = pyglet.resource.image('res/PNG/GUI/pa_down2.png')
    class Down(glooey.Background):
        custom_image = pyglet.resource.image('res/PNG/GUI/pa_down2.png')
class Start_New_Button(TitleScreen_Button):
    def __init__(self, text, client):
        super().__init__(text)
        self.client = client          

stack = glooey.Stack()
stack.custom_alignment = 'fill'
bg = glooey.Image(pyglet.image.load("res/PNG/GUI/title menu.png"))
bg.custom_alignment = 'fill'
stack.add(bg)
board = glooey.Board()
board.custom_alignment = 'fill'

vbox = TitleScreen_Grid()
vbox.alignment = 'right'
stack.add(vbox)

class Main_Window2(pyglet.window.Window):
    def __init__(self, width, height):
        conf = Config(sample_buffers=1,
                      samples=4,
                      depth_size=16,
                      double_buffer=True)
        super(Main_Window2, self).__init__(Game.WIDTH, Game.HEIGHT, config=conf)
        self.push_handlers(keys)

        self.gui = glooey.Gui(self, gui_batch)
        
        self.client = Game_Client2(width, height, self.gui, stack)
        start_button = Start_Button(self.client)
        start_button.right_padding = 170
        vbox.add(start_button)
        vbox.top_padding = 250
        exit_button = Exit_Button()
        exit_button.right_padding = 170
        def exit(widget):
            sys.exit()
        exit_button.on_click = exit
        vbox.add(exit_button)
        self.gui.add(stack)

        self.ping = pyglet.text.HTMLLabel(
            '<font face="Arial" size="13" color="white"><b>latency: %3.3f ms fps:%3.3f</b></font>' % (self.client._client.latency, pyglet.clock.get_fps()),
            x=self.width-130, y=self.height-12,
            anchor_x='center', anchor_y='center')
    def on_draw(self):
        self.clear()
        if self.client.running:
            self.client.update_camera_player()
            self.client.camera.apply_World()
            bg_batch.draw()
            fg_batch.draw()
            for t in tanks.values():
                if t.alive:
                    t.hp_bar.draw()
            self.client.camera.apply_Hud()
            self.client.hud.draw()
            hud_batch.draw()
            self.client.minimap.update()
            self.ping = pyglet.text.HTMLLabel(
            '<font face="Arial" size="13" color="white"><b>latency: %3.3f ms fps:%3.3f</b></font>' % (self.client._client.latency, pyglet.clock.get_fps()),
            x=self.width-130, y=self.height-12,
            anchor_x='center', anchor_y='center')
            self.ping.draw()
            self.get_input()
        gui_batch.draw()

    def get_input(self):
        if keys[key._1]:
            self.client.switch1()
        elif keys[key._2]:
            self.client.switch2()
        if keys[key.J]:
            self.client.rotate_left_turret()
        elif keys[key.L]:
            self.client.rotate_right_turret()
        else:
            self.client.stop_rotate_turret()
        if keys[key.W]:
            self.client.move_forward()
        elif keys[key.S]:
            self.client.move_backward()
        else:
            self.client.stop()
        if keys[key.D]:
            self.client.rotate_right()
        elif keys[key.A]:
            self.client.rotate_left()
        else:
            self.client.stop_rotate()
        if keys[key.K] and not self.client.tank.isReloading:
            self.client.fire()

class Game_Client2:
    def __init__(self, width, height, gui, stack):
        self.logger = logging.getLogger('Client')
        hdlr = logging.FileHandler('tankwarz_client.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.INFO)

        self.running = False
        self.started = False
        self.connected = False
        self.alive = True
        
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

        self.cl_id = int(time.time())
        self.CLIENT_ID = int(time.time())
        self.gui = gui
        self.stack = stack
        self._client = legume.Client()

        self._client.OnMessage += self.message_handler
        self._client.OnConnectRequestAccepted += self.on_connect_accepted
        self._client.OnConnectRequestRejected += self.on_connect_rejected
        self._client.OnError += self.on_connection_error
        self._client.OnDisconnect += self.on_disconnect
        self.update_timer = time.time()
        self.time_label = pyglet.text.HTMLLabel(
            '<font face="Arial" size="50" color="white"><b>00:00</b></font>',
            x=Game.WIDTH//2, y=Game.HEIGHT-12,
            anchor_x='center', anchor_y='center', batch=hud_batch)
        self.score = 0
        create_walls()
        pyglet.clock.schedule_interval(self.update, 1.0/60)
    def on_connect_accepted(self,sender, args):
        self.connected = True
        self.logger.info("Connection Accepted")
        if not self.started:
            self.logger.info("Creating New Tank")
            cl = ClientStart()
            cl.client_id.value = self.CLIENT_ID
            self._client.send_reliable_message(cl)
            message = TankCreate()
            message.id.value = self.cl_id
            x = random.randint(660, 2230)
            y = random.randint(350, 2500)
            message.pos_x.value = x
            message.pos_y.value = y
            message.rot.value = 0
            message.l_vel_x.value = 0
            message.l_vel_y.value = 0
            message.a_vel.value = 0
            color_value = random.randint(1,5)
            message.color.value = color_value
            message.client_id.value = self.CLIENT_ID
            self._client.send_reliable_message(message)
            self.started = True

    def on_connect_rejected(self,args):
        self.logger.info("Connection Rejected")
    def on_disconnect(self, sender, args):
        self.logger.info("You have been disconnected")
    def on_connection_error(self, sender, error_message):
        self.logger.error(error_message)
        self.logger.info("Attempting to reconnect")
        self.connect(host)
    def start_game(self):
        self.logger.info("STARTGAME")
        self.tank = tanks[self.cl_id]
        self.hud = Hud()
        self.camera = Camera()
        self.camera.init_gl(Game.WIDTH, Game.HEIGHT)
        self.on_resize = self.camera.on_resize
        self.bg_player.play()   
        self.running = True
        self.gui.remove(self.stack)

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

    def switch1(self):
        if self.tank.ammo_type == Projectile.Ammo_Type.AP:
            self.switch_sound.play()
            self.tank.ammo_type = Projectile.Ammo_Type.REGULAR
            self.hud.bullet1_overlay.color = (40,40,40,200)
            self.hud.bullet1_sprite.opacity = 255
            self.hud.bullet1_text.color = (255,255,255,255)
            self.hud.bullet1_ammo.color = (255,255,255,255)
            self.hud.bullet2_overlay.color = (40,40,40,100)
            self.hud.bullet2_sprite.opacity = 100
            self.hud.bullet2_text.color = (255,255,255,100)
            self.hud.bullet2_ammo.color = (255,255,255,100)
            msg = TankSwitchAmmo()
            msg.id.value = self.tank.idn
            msg.ammo_type.value = self.tank.ammo_type
            self.send_reliable_message_safely(msg)

    def switch2(self):
        if self.tank.ammo_type == Projectile.Ammo_Type.REGULAR:
            self.switch_sound.play()
            self.tank.ammo_type = Projectile.Ammo_Type.AP
            self.hud.bullet1_overlay.color = (40,40,40,100)
            self.hud.bullet1_sprite.opacity = 100
            self.hud.bullet1_text.color = (255,255,255,100)
            self.hud.bullet1_ammo.color = (255,255,255,100) 
            self.hud.bullet2_overlay.color = (40,40,40,200)
            self.hud.bullet2_sprite.opacity = 255
            self.hud.bullet2_text.color = (255,255,255,255)
            self.hud.bullet2_ammo.color = (255,255,255,255)
            msg = TankSwitchAmmo()
            msg.id.value = self.tank.idn
            msg.ammo_type.value = self.tank.ammo_type
            self.send_reliable_message_safely(msg)

    def rotate_left_turret(self):
        self.tank.rotateTurret(Direction.LEFT)  
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.TURRET_ROTATE_LEFT
        self.send_message_safely(msg)
    def rotate_right_turret(self):
        self.tank.rotateTurret(Direction.RIGHT)
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.TURRET_ROTATE_RIGHT
        self.send_message_safely(msg)
    def stop_rotate_turret(self):
        self.tank.stopRotateTurret()
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.STOP_ROTATING_TURRET
        self.send_message_safely(msg)
    def move_forward(self):
        self.tank.move(Direction.FORWARD)
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.MOVE_FORWARD
        self.send_message_safely(msg)
    def move_backward(self):
        self.tank.move(Direction.BACKWARD)
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.MOVE_BACKWARD
        self.send_message_safely(msg)
    def stop(self):
        self.tank.stop()
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.STOP_MOVING
        self.send_message_safely(msg)
    def rotate_right(self):
        self.tank.rotate(Direction.RIGHT)
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.ROTATE_RIGHT
        self.send_message_safely(msg)
    def rotate_left(self):
        self.tank.rotate(Direction.LEFT)
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.ROTATE_LEFT
        self.send_message_safely(msg)
    def stop_rotate(self):
        self.tank.stopRotating()
        msg = TankCommand()
        msg.id.value = self.cl_id
        msg.command.value = Tank.Command.STOP_ROTATING
        self.send_message_safely(msg)
    def fire(self):
        if self.tank.isReloading:
            return
        self.tank.reloading = True
        msg = TankFire()
        msg.id.value = self.cl_id
        msg.projectile_id.value = int(time.time())
        self.tank.fire(msg.projectile_id.value)
        self.send_message_safely(msg)
        if self.tank.ammo_type == Projectile.Ammo_Type.REGULAR and self.tank.ammo1 <= 0 or self.tank.ammo_type == Projectile.Ammo_Type.AP and self.tank.ammo2 <= 0:
            return
        Tank.firing_sound.play()
        Tank.reloading_sound.play()
        self.hud.update(self.tank.ammo1, self.tank.ammo2)
    def send_message_safely(self, msg):
        try:
            self._client.send_message(msg)
        except legume.exceptions.ClientError:
            self.connected = False
            if self._client.connected:
                self._client.send_message(msg)
    def send_reliable_message_safely(self, msg):
        try:
            self._client.send_message(msg)
        except legume.exceptions.ClientError:
            self.connected = False
            if self._client.connected:
                self._client.send_reliable_message(msg)
    def update(self, dt):
        dtt = 1.0/60.0
        space.step(dtt)
        for tank in tanks.values():
            tank.update(dtt)
        for p in projectiles.values():
            p.update(dtt)

    def message_handler(self, sender, message):
        if legume.messages.message_factory.is_a(message, 'TankCreate'):
            if tanks.get(message.id.value) is None:
                tanks[message.id.value] = Tank.create_from_message(message)
                if message.id.value == self.cl_id:
                    self.logger.info("Creating self")
                    self.start_game()
            else:
                tanks[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'TankUpdate'):
            if tanks.get(message.id.value) is None:
                tanks[message.id.value] = Tank.create_from_message(message)
                if message.id.value == self.cl_id:
                    self.logger.info("Creating self")
                    self.start_game()
            else:
                tanks[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'GameOver'):
            if message.winner_id.value == self.CLIENT_ID:
                game_over_bg = glooey.Background()
                game_over_bg.image = pyglet.image.load("res/PNG/GUI/overlay.png")
                game_over_bg.custom_alignment = 'fill'
                self.gui.add(game_over_bg)
                game_over_vbox = glooey.VBox()
                game_over_vbox.custom_alignment = 'center'
                game_over_label = TitleLabel("You Win!")
                score_label = SubtitleLabel("Your score is %d" % message.score.value)
                score_label.custom_font_size = 10
                ex_button = Exit_Button()
                game_over_vbox.add(game_over_label)
                game_over_vbox.add(score_label)
                game_over_vbox.add(ex_button)
                self.gui.add(game_over_vbox)
            else:
                game_over_bg = glooey.Background()
                game_over_bg.image = pyglet.image.load("res/PNG/GUI/overlay.png")
                game_over_bg.custom_alignment = 'fill'
                self.gui.add(game_over_bg)
                game_over_vbox = glooey.VBox()
                game_over_vbox.custom_alignment = 'center'
                game_over_label = TitleLabel("You Lose")
                ex_button = Exit_Button()
                game_over_vbox.add(game_over_label)
                game_over_vbox.add(ex_button)
                self.gui.add(game_over_vbox)
        elif legume.messages.message_factory.is_a(message, 'UpdateTime'):
            time = message.time.value  
            self.time_label.text = '<font face="Arial" size="50" color="white"><b>%s</b></font>' % (time)   
        elif legume.messages.message_factory.is_a(message, 'TankFireClient'):
            tank = tanks[message.id.value]
            if tank.idn != self.tank.idn:
                tank.fire(message.projectile_id.value)
        elif legume.messages.message_factory.is_a(message, 'TankSwitchAmmo'):
            tank = tanks[message.id.value]
            tank.ammo_type = message.ammo_type.value
        elif legume.messages.message_factory.is_a(message, 'TankHit'):
            tank = tanks[message.id.value]
            projectile = projectiles.get(message.projectile_id.value)
            if projectile is not None:
                tank.hit(projectile.damage)
                if tank.idn == self.tank.idn and not self.tank.alive and not self.tank.destroyed:
                    self.tank.destroyed = True
                    game_over_bg = glooey.Background()
                    game_over_bg.image = pyglet.image.load("res/PNG/GUI/overlay.png")
                    game_over_bg.custom_alignment = 'fill'
                    self.gui.add(game_over_bg)
                    game_over_vbox = glooey.VBox()
                    game_over_vbox.alignment = 'center'
                    game_over_label = TitleLabel("You have been eliminated")
                    retry_button = PlayAgain_Button()
                    ex_button = Exit_Button()
                    def on_click(widget):
                        self.gui.remove(game_over_bg)
                        self.gui.remove(game_over_vbox)
                        self.gui.add(stack)
                        self._client.disconnect()
                        self.cl_id = random.randint(1,100000)
                        self.started = False
                        self.running = False
                    retry_button.on_click = on_click
                    game_over_vbox.add(game_over_label)
                    game_over_vbox.add(retry_button)
                    game_over_vbox.add(ex_button)
                    self.gui.add(game_over_vbox)
                projectile.destroy()
                projectiles.pop(projectile.idn)

        elif legume.messages.message_factory.is_a(message, 'ProjectileDestroy'):
            projectile = projectiles.get(message.projectile_id.value)
            if projectile is not None:
                projectile.destroy()
                projectiles.pop(projectile.idn)
        elif legume.messages.message_factory.is_a(message, 'ProjectileCreate'):
            if projectiles.get(message.id.value) is None:
                projectiles[message.id.value] = Projectile.create_from_message(message)
            else:
                projectiles[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'ProjectileUpdate'):
            if projectiles.get(message.id.value) is None:
                projectiles[message.id.value] = Projectile.create_from_message(message)
            else:
                projectiles[message.id.value].update_from_message(message)
        elif legume.messages.message_factory.is_a(message, 'MapCreate'):
            l = message.l.value
            w = message.w.value
            seed_a = message.seed_a.value
            seed_b = message.seed_b.value
            self.game_map = Game_Map.generate_map(l,w, seed_a, seed_b)
            self.minimap = Minimap(self.game_map, self.cl_id)
        else:
            self.logger.info('Message: %s' % message)

    def connect(self, host='localhost'):
        self._client.connect((host, PORT))

    def send_update(self):
        if self.tank is not None:
            self.client.send_message_safely(self.tank.get_message())
        for projectile in projectiles.values():
            self.client.send_message_safely(projectile.get_message())
        
    def go(self, args):
        try:
            if time.time() > self.update_timer + UPDATE_RATE:
                self.update_timer = time.time()
            self._client.update()
        except:
            self.running = False
        
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

if __name__ == '__main__':
    game1 = Main_Window2(Game.WIDTH, Game.HEIGHT) 
    pyglet.clock.schedule_interval(game1.client.go, 0.0001)
    pyglet.app.run()