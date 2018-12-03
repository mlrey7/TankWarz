#!/usr/bin/env python

__version__ = '0.3.0'

from .shapes import Shape, Vector, Rect
from .shapes import cast_anything_to_vector
from .shapes import cast_anything_to_rectangle
from .shapes import cast_shape_to_rectangle
from .shapes import accept_anything_as_vector
from .shapes import accept_anything_as_rectangle
from .shapes import accept_shape_as_rectangle
from .shapes import golden_ratio
from .shapes import get_distance
from .shapes import interpolate
from .shapes import NullVectorError
from .shapes import VectorCastError
from .shapes import RectangleCastError
