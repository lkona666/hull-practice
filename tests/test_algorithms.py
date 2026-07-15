import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Теперь импортируй свои модули
from algorithms import graham_scan, jarvis_march, orientation
from geometry import perimeter, area

# Вспомогательный класс Point (если у тебя его нет в отдельном модуле)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"


# === ТЕСТЫ ДЛЯ ORIENTATION ===

def test_orientation_left_turn():
    """Тест: левый поворот (против часовой стрелки)"""
    p = Point(0, 0)
    q = Point(1, 0)
    r = Point(1, 1)
    assert orientation(p, q, r) == 1


def test_orientation_right_turn():
    """Тест: правый поворот (по часовой стрелке)"""
    p = Point(0, 0)
    q = Point(1, 0)
    r = Point(1, -1)
    assert orientation(p, q, r) == -1


def test_orientation_collinear():
    """Тест: точки на одной прямой"""
    p = Point(0, 0)
    q = Point(1, 1)
    r = Point(2, 2)
    assert orientation(p, q, r) == 0


# === ТЕСТЫ ДЛЯ GRAHAM SCAN ===

def test_graham_triangle():
    """Тест: треугольник — все три точки на оболочке"""
    points = [Point(0, 0), Point(1, 0), Point(0, 1)]
    hull, stats = graham_scan(points)
    assert len(hull) == 3
    assert stats['h'] == 3


def test_graham_square():
    """Тест: квадрат — все четыре точки на оболочке"""
    points = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    hull, stats = graham_scan(points)
    assert len(hull) == 4


def test_graham_with_interior_point():
    """Тест: точка внутри не попадает на оболочку"""
    points = [
        Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2),  # квадрат
        Point(1, 1)  # точка внутри
    ]
    hull, stats = graham_scan(points)
    assert len(hull) == 4  # только 4 угловые точки
    assert Point(1, 1) not in hull


def test_graham_single_point():
    """Тест: одна точка"""
    points = [Point(5, 5)]
    hull, stats = graham_scan(points)
    assert len(hull) == 1


def test_graham_two_points():
    """Тест: две точки"""
    points = [Point(0, 0), Point(1, 1)]
    hull, stats = graham_scan(points)
    assert len(hull) == 2


# === ТЕСТЫ ДЛЯ JARVIS MARCH ===

def test_jarvis_triangle():
    """Тест: треугольник"""
    points = [Point(0, 0), Point(1, 0), Point(0, 1)]
    hull, stats = jarvis_march(points)
    assert len(hull) == 3


def test_jarvis_square():
    """Тест: квадрат"""
    points = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    hull, stats = jarvis_march(points)
    assert len(hull) == 4


def test_jarvis_with_interior_point():
    """Тест: точка внутри не попадает на оболочку"""
    points = [
        Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2),
        Point(1, 1)
    ]
    hull, stats = jarvis_march(points)
    assert len(hull) == 4


# === ТЕСТЫ ДЛЯ PERIMETER И AREA ===

def test_perimeter_square():
    """Тест: периметр квадрата со стороной 1"""
    hull = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    p = perimeter(hull)
    assert abs(p - 4.0) < 0.001


def test_area_square():
    """Тест: площадь квадрата со стороной 1"""
    hull = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    a = area(hull)
    assert abs(a - 1.0) < 0.001


def test_area_triangle():
    """Тест: площадь треугольника"""
    hull = [Point(0, 0), Point(4, 0), Point(0, 3)]
    a = area(hull)
    assert abs(a - 6.0) < 0.001  # площадь = 0.5 * 4 * 3 = 6


# === ТЕСТ СРАВНЕНИЯ АЛГОРИТМОВ ===

def test_algorithms_give_same_result():
    """Тест: оба алгоритма дают одинаковый результат"""
    points = [
        Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1),
        Point(0.5, 0.5)
    ]
    hull_g, _ = graham_scan(points)
    hull_j, _ = jarvis_march(points)
    assert len(hull_g) == len(hull_j)