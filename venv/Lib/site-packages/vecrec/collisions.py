#!/usr/bin/env python

def circle_touching_line(center, radius, start, end):
    """ Return true if the given circle intersects the given segment.  Note 
    that this checks for intersection with a line segment, and not an actual 
    line.

    :param center: Center of the circle.
    :type center: Vector
    :param radius: Radius of the circle.
    :type radius: float
    :param start: The first end of the line segment.
    :type start: Vector
    :param end: The second end of the line segment.
    :type end: Vector
    """

    C, R = center, radius
    A, B = start, end

    a = (B.x - A.x)**2 + (B.y - A.y)**2
    b = 2 * (B.x - A.x) * (A.x - C.x)       \
            + 2 * (B.y - A.y) * (A.y - C.y)
    c = C.x**2 + C.y**2 + A.x**2 + A.y**2   \
            - 2 * (C.x * A.x + C.y * A.y) - R**2

    discriminant = b**2 - 4 * a * c

    if discriminant < 0:
        return False
    elif discriminant == 0:
        u = v = -b / float(2 * a)
    else:
        u = (-b + math.sqrt(discriminant)) / float(2 * a)
        v = (-b - math.sqrt(discriminant)) / float(2 * a)

    if u < 0 and v < 0: return False
    if u > 1 and v > 1: return False

    return True


