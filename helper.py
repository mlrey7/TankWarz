import pyglet
class Rectangle:
    def __init__(self,lx,ly, width, height, color=(0,0,0,0)):
        self.width = width
        self.height = height
        self.lx = lx 
        self.ly = ly 
        self.vertices = ('v2i', (int(self.lx), int(self.ly), int(self.lx), int(self.lx+self.height),
         int(self.lx+self.width), int(self.ly+self.height), int(self.lx+self.width),int(self.ly)))
        self.vertice_color = ('c4B', (color[0],color[1],color[2],color[3], 
                                    color[0],color[1],color[2],color[3],
                                     color[0],color[1],color[2],color[3], 
                                     color[0],color[1],color[2],color[3]))
        self.color = color
    def draw(self):
        self.vertices = ('v2i', (int(self.lx), int(self.ly), int(self.lx), int(self.ly+self.height),
         int(self.lx+self.width), int(self.ly+self.height), int(self.lx+self.width),int(self.ly)))
        self.vertice_color = ('c4B', (self.color[0],self.color[1],self.color[2],self.color[3], 
                                   self. color[0],self.color[1],self.color[2],self.color[3],
                                     self.color[0],self.color[1],self.color[2],self.color[3], 
                                     self.color[0],self.color[1],self.color[2],self.color[3]))
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self.vertices, self.vertice_color)