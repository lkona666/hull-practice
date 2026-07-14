<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Консольная версия для Docker"""
import json
import sys
import os
import math

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

def orientation(p, q, r):
    val = (q.x - p.x) * (r.y - p.y) - (r.x - p.x) * (q.y - p.y)
    if val > 1e-9: return 1
    elif val < -1e-9: return -1
    return 0

def dist_sq(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

def graham_scan(points):
    if len(points) < 3:
        return list(points), {"ops": 0, "h": len(points)}
    p0 = min(points, key=lambda p: (p.y, p.x))
    others = [p for p in points if not (p == p0)]
    others.sort(key=lambda p: (math.atan2(p.y - p0.y, p.x - p0.x), dist_sq(p0, p)))
    hull = [p0, others[0]]
    ops = 0
    for p in others[1:]:
        while len(hull) >= 2:
            ops += 1
            if orientation(hull[-2], hull[-1], p) != 1:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull, {"ops": ops, "h": len(hull)}

def jarvis_march(points):
    if len(points) < 3:
        return list(points), {"ops": 0, "h": len(points)}
    start = min(points, key=lambda p: (p.x, p.y))
    hull = []
    current = start
    ops = 0
    while True:
        hull.append(current)
        endpoint = None
        for q in points:
            ops += 1
            if q == current: continue
            if endpoint is None:
                endpoint = q
                continue
            o = orientation(current, endpoint, q)
            if o == 1:
                endpoint = q
            elif o == 0 and dist_sq(current, q) > dist_sq(current, endpoint):
                endpoint = q
        current = endpoint
        if current == start: break
    return hull, {"ops": ops, "h": len(hull)}

def perimeter(hull):
    if len(hull) < 2: return 0.0
    total = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        total += math.sqrt(dist_sq(hull[i], hull[j]))
    return total

def area(hull):
    if len(hull) < 3: return 0.0
    s = 0.0
    n = len(hull)
    for i in range(n):
        j = (i + 1) % n
        s += hull[i].x * hull[j].y
        s -= hull[j].x * hull[i].y
    return abs(s) / 2.0

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/sample.json"
    
    print("=" * 60)
    print("  ВЫПУКЛАЯ ОБОЛОЧКА — Вариант А-24")
    print("  Медведев Д.В., группа БИН-24-1")
    print("=" * 60)
    print()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    points = [Point(item['x'], item['y']) for item in data]
    
    print(f"Загружено {len(points)} точек из {input_file}")
    print()
    
    hull_g, stats_g = graham_scan(points)
    print("=== Сканирование Грэхема ===")
    print(f"  Вершин оболочки: {stats_g['h']}")
    print(f"  Операций выполнено: {stats_g['ops']}")
    print(f"  Периметр: {perimeter(hull_g):.3f}")
    print(f"  Площадь: {area(hull_g):.3f}")
    print()
    
    hull_j, stats_j = jarvis_march(points)
    print("=== Обход Джарвиса ===")
    print(f"  Вершин оболочки: {stats_j['h']}")
    print(f"  Операций выполнено: {stats_j['ops']}")
    print(f"  Периметр: {perimeter(hull_j):.3f}")
    print(f"  Площадь: {area(hull_j):.3f}")
    print()
    
    print("=== Сравнение ===")
    if stats_g['ops'] < stats_j['ops']:
        print(f"  Грэхем эффективнее ({stats_g['ops']} против {stats_j['ops']})")
    else:
        print(f"  Джарвис эффективнее ({stats_j['ops']} против {stats_g['ops']})")
    print()
    print("Вершины выпуклой оболочки:")
    for i, p in enumerate(hull_g, 1):
        print(f"  {i}. ({p.x:.1f}, {p.y:.1f})")

if __name__ == "__main__":
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Консольная версия для Docker"""
import json
import sys
import os
import math

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

def orientation(p, q, r):
    val = (q.x - p.x) * (r.y - p.y) - (r.x - p.x) * (q.y - p.y)
    if val > 1e-9: return 1
    elif val < -1e-9: return -1
    return 0

def dist_sq(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

def graham_scan(points):
    if len(points) < 3:
        return list(points), {"ops": 0, "h": len(points)}
    p0 = min(points, key=lambda p: (p.y, p.x))
    others = [p for p in points if not (p == p0)]
    others.sort(key=lambda p: (math.atan2(p.y - p0.y, p.x - p0.x), dist_sq(p0, p)))
    hull = [p0, others[0]]
    ops = 0
    for p in others[1:]:
        while len(hull) >= 2:
            ops += 1
            if orientation(hull[-2], hull[-1], p) != 1:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull, {"ops": ops, "h": len(hull)}

def jarvis_march(points):
    if len(points) < 3:
        return list(points), {"ops": 0, "h": len(points)}
    start = min(points, key=lambda p: (p.x, p.y))
    hull = []
    current = start
    ops = 0
    while True:
        hull.append(current)
        endpoint = None
        for q in points:
            ops += 1
            if q == current: continue
            if endpoint is None:
                endpoint = q
                continue
            o = orientation(current, endpoint, q)
            if o == 1:
                endpoint = q
            elif o == 0 and dist_sq(current, q) > dist_sq(current, endpoint):
                endpoint = q
        current = endpoint
        if current == start: break
    return hull, {"ops": ops, "h": len(hull)}

def perimeter(hull):
    if len(hull) < 2: return 0.0
    total = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        total += math.sqrt(dist_sq(hull[i], hull[j]))
    return total

def area(hull):
    if len(hull) < 3: return 0.0
    s = 0.0
    n = len(hull)
    for i in range(n):
        j = (i + 1) % n
        s += hull[i].x * hull[j].y
        s -= hull[j].x * hull[i].y
    return abs(s) / 2.0

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/sample.json"
    
    print("=" * 60)
    print("  ВЫПУКЛАЯ ОБОЛОЧКА — Вариант А-24")
    print("  Медведев Д.В., группа БИН-24-1")
    print("=" * 60)
    print()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    points = [Point(item['x'], item['y']) for item in data]
    
    print(f"Загружено {len(points)} точек из {input_file}")
    print()
    
    hull_g, stats_g = graham_scan(points)
    print("=== Сканирование Грэхема ===")
    print(f"  Вершин оболочки: {stats_g['h']}")
    print(f"  Операций выполнено: {stats_g['ops']}")
    print(f"  Периметр: {perimeter(hull_g):.3f}")
    print(f"  Площадь: {area(hull_g):.3f}")
    print()
    
    hull_j, stats_j = jarvis_march(points)
    print("=== Обход Джарвиса ===")
    print(f"  Вершин оболочки: {stats_j['h']}")
    print(f"  Операций выполнено: {stats_j['ops']}")
    print(f"  Периметр: {perimeter(hull_j):.3f}")
    print(f"  Площадь: {area(hull_j):.3f}")
    print()
    
    print("=== Сравнение ===")
    if stats_g['ops'] < stats_j['ops']:
        print(f"  Грэхем эффективнее ({stats_g['ops']} против {stats_j['ops']})")
    else:
        print(f"  Джарвис эффективнее ({stats_j['ops']} против {stats_g['ops']})")
    print()
    print("Вершины выпуклой оболочки:")
    for i, p in enumerate(hull_g, 1):
        print(f"  {i}. ({p.x:.1f}, {p.y:.1f})")

if __name__ == "__main__":
>>>>>>> 5fd4d7eea2ac6baab0f6de9122979f5c776c18e3
    main()