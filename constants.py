from enum import Enum
from enum import IntEnum


class Game(IntEnum):
    WIDTH = 1280
    HEIGHT = 700
class Direction(IntEnum):
    FORWARD = 1
    BACKWARD = -1
    RIGHT = 1
    LEFT = -1
class Color(Enum):
    BLACK = "Black"
    BLUE = "Blue"
    GREEN = "Green"
    RED = "Red"
    BEIGE = "Beige"
    
    def to_int(c):
        return IntColor[c]
    def from_int(c):
        return ColorInt[c]

ColorInt = {1 : Color.BLACK,
        2 : Color.BLUE,
        3 : Color.GREEN,
        4 : Color.RED,
        5 : Color.BEIGE}

IntColor = {Color.BLACK : 1,
        Color.BLUE : 2,
        Color.GREEN : 3,
        Color.RED : 4,
        Color.BEIGE : 5}       
class Coll_Type(IntEnum):
    TANK = 1
    PROJECTILE = 2
    ENVIRONMENT = 3
    CRATE = 4
    AMMO = 5


