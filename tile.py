from enum import Enum

class Tile:
    class Type(Enum):
        DIRT = "dirt"
        GRASS = "grass"
        SAND = "sand"
        TEMPERATE = "temperate"
        SHRUB =  "shrub"
        WATER = "water"
        DARKSAND = 'darksand'
    def __init__(self, tile_type):
        self.tile_type = tile_type