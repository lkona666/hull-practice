import math


def dist_sq(a, b):
    """Квадрат расстояния между точками."""
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def perimeter(hull):
    """Периметр выпуклой оболочки."""
    if len(hull) < 2:
        return 0.0
    total = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        dx = hull[i].x - hull[j].x
        dy = hull[i].y - hull[j].y
        total += math.sqrt(dx * dx + dy * dy)
    return total


def area(hull):
    """Площадь выпуклой оболочки по формуле Гаусса."""
    if len(hull) < 3:
        return 0.0
    s = 0.0
    n = len(hull)
    for i in range(n):
        j = (i + 1) % n
        s += hull[i].x * hull[j].y
        s -= hull[j].x * hull[i].y
    return abs(s) / 2.0