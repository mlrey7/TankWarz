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