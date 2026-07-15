import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if other is None:
            return False
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

    def __hash__(self):
        return hash((round(self.x, 9), round(self.y, 9)))

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


def orientation(p, q, r):
    """Возвращает 1 (левый поворот), -1 (правый), 0 (коллинеарны)."""
    val = (q.x - p.x) * (r.y - p.y) - (r.x - p.x) * (q.y - p.y)
    if val > 1e-9:
        return 1
    elif val < -1e-9:
        return -1
    return 0


def dist_sq(a, b):
    """Квадрат расстояния между точками."""
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def graham_scan(points, on_step=None):
    """Сканирование Грэхема. Возвращает (hull, stats)."""
    ops = 0
    if len(points) < 3:
        return list(points), {"ops": 0, "h": len(points)}

    p0 = min(points, key=lambda p: (p.y, p.x))
    others = [p for p in points if p != p0]

    others.sort(key=lambda p: (
        math.atan2(p.y - p0.y, p.x - p0.x),
        dist_sq(p0, p)
    ))

    hull = [p0, others[0]]
    for p in others[1:]:
        while len(hull) >= 2:
            ops += 1
            if orientation(hull[-2], hull[-1], p) != 1:
                hull.pop()
            else:
                break
        hull.append(p)

    return hull, {"ops": ops, "h": len(hull)}


def jarvis_march(points, on_step=None):
    """Обход Джарвиса. Возвращает (hull, stats)."""
    ops = 0
    if len(points) < 3:
        return list(points), {"ops": 0, "h": len(points)}

    start = min(points, key=lambda p: (p.x, p.y))
    hull = []
    current = start

    while True:
        hull.append(current)
        endpoint = None
        for q in points:
            ops += 1
            if q == current:
                continue
            if endpoint is None:
                endpoint = q
                continue
            o = orientation(current, endpoint, q)
            if o == 1:
                endpoint = q
            elif o == 0:
                d1 = dist_sq(current, q)
                d2 = dist_sq(current, endpoint)
                if d1 > d2:
                    endpoint = q
        current = endpoint
        if current == start:
            break

    return hull, {"ops": ops, "h": len(hull)}