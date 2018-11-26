import pyglet
from pyglet.window import key
from pyglet.gl import *
from constants import *

class Camera(object):
    """ A camera.
    """
    def __init__(self):
        self.left   = 0
        self.right  = Game.WIDTH
        self.bottom = 0
        self.top    = Game.HEIGHT
        self.zoom_level = 1
        self.width  = Game.WIDTH
        self.height = Game.HEIGHT
        self.zoomed_width  = Game.WIDTH
        self.zoomed_height = Game.HEIGHT

    def init_gl(self, width, height):
        # Set clear color
        glClearColor(0/255, 0/255, 0/255, 0/255)

        # Set antialiasing
        glEnable( GL_LINE_SMOOTH )
        glEnable( GL_POLYGON_SMOOTH )
        glHint( GL_LINE_SMOOTH_HINT, GL_NICEST )

        # Set alpha blending
        glEnable( GL_BLEND )
        glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

        # Set viewport
        glViewport( 0, 0, width, height )

    def on_resize(self, width, height):
        """ Adjust window size.
        """
        self.width, self.height = width, height
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        # If zoom_level is in the proper range
        if .2 < self.zoom_level*f < 5:

            self.zoom_level *= f

            mouse_x = x/self.width
            mouse_y = y/self.height

            mouse_x_in_world = self.left   + mouse_x*self.zoomed_width
            mouse_y_in_world = self.bottom + mouse_y*self.zoomed_height

            self.zoomed_width  *= f
            self.zoomed_height *= f

            self.left   = mouse_x_in_world - mouse_x*self.zoomed_width
            self.right  = mouse_x_in_world + (1 - mouse_x)*self.zoomed_width
            self.bottom = mouse_y_in_world - mouse_y*self.zoomed_height
            self.top    = mouse_y_in_world + (1 - mouse_y)*self.zoomed_height

    def apply_World(self):
        """ Apply camera transformation.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.left, self.right, self.bottom, self.top, 1, -1 )
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def apply_Hud(self):
        """ Apply camera transformation.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, 1, -1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()