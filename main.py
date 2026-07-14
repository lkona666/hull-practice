#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Учебная практика 2026 — Вариант А-24
Выпуклая оболочка: алгоритмы Грэхема и Джарвиса
Студент: Медведев Даниил Владимирович, группа БИН-24-1
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
import math
import os
import time
import threading

# ===== АЛГОРИТМИЧЕСКОЕ ЯДРО =====

class Point:
    """Точка на плоскости."""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __eq__(self, other):
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9

    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f})"

    def __hash__(self):
        return hash((round(self.x, 6), round(self.y, 6)))


def orientation(p, q, r):
    """
    Определяет ориентацию тройки точек.
    Возвращает:
      1  — левый поворот (против часовой стрелки)
     -1  — правый поворот (по часовой стрелке)
      0  — точки коллинеарны
    """
    val = (q.x - p.x) * (r.y - p.y) - (r.x - p.x) * (q.y - p.y)
    if val > 1e-9:
        return 1
    elif val < -1e-9:
        return -1
    return 0


def dist_sq(a, b):
    """Квадрат расстояния между точками."""
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


class ConvexHull:
    """Класс с реализацией обоих алгоритмов."""

    @staticmethod
    def graham_scan(points, on_step=None):
        """
        Сканирование Грэхема.
        on_step — функция, вызываемая после каждого шага для анимации.
        Возвращает (hull, stats).
        """
        ops = 0
        steps = []

        if len(points) < 3:
            hull = list(points)
            if on_step:
                on_step("Исходные точки", points, hull, [], 0)
            return hull, {"ops": 0, "h": len(hull)}

        # 1. Находим самую нижнюю (и самую левую при равенстве) точку
        p0 = min(points, key=lambda p: (p.y, p.x))
        others = [p for p in points if not (p == p0)]

        if on_step:
            on_step(f"Стартовая точка: {p0}", points, [p0], [p0], ops)

        # 2. Сортируем остальные точки по полярному углу относительно p0
        def sort_key(p):
            # Сначала по углу (через ориентацию с горизонтальным лучом), потом по расстоянию
            # Используем atan2 для наглядности
            angle = math.atan2(p.y - p0.y, p.x - p0.x)
            return (angle, dist_sq(p0, p))

        others.sort(key=sort_key)
        ops += len(others) * 2  # учтём операции сортировки

        if on_step:
            on_step("Точки отсортированы по углу", points, [p0], [], ops)

        # 3. Проходим по отсортированным точкам, используя стек
        hull = [p0, others[0]]

        for i, p in enumerate(others[1:], start=2):
            # Удаляем точки, которые создают "правый поворот"
            while len(hull) >= 2:
                ops += 1
                if orientation(hull[-2], hull[-1], p) != 1:
                    removed = hull.pop()
                    if on_step:
                        on_step(f"Удаляем {removed} (правый поворот)", points, list(hull), [p], ops)
                else:
                    break
            hull.append(p)
            if on_step:
                on_step(f"Добавляем {p} в оболочку", points, list(hull), [p], ops)

        return hull, {"ops": ops, "h": len(hull)}

    @staticmethod
    def jarvis_march(points, on_step=None):
        """
        Обход Джарвиса (gift wrapping).
        on_step — функция, вызываемая после каждого шага для анимации.
        Возвращает (hull, stats).
        """
        ops = 0

        if len(points) < 3:
            hull = list(points)
            if on_step:
                on_step("Исходные точки", points, hull, [], 0)
            return hull, {"ops": 0, "h": len(hull)}

        # 1. Находим самую левую (и самую нижнюю) точку
        start = min(points, key=lambda p: (p.x, p.y))
        hull = []
        current = start

        if on_step:
            on_step(f"Стартовая точка: {current}", points, [current], [current], ops)

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
                if o == 1:  # q левее
                    endpoint = q
                elif o == 0:  # коллинеарны — берём самую дальнюю
                    if dist_sq(current, q) > dist_sq(current, endpoint):
                        endpoint = q

            if on_step:
                on_step(f"Добавляем {endpoint}", points, list(hull) + [endpoint], [endpoint], ops)

            current = endpoint
            if current == start:
                break

        return hull, {"ops": ops, "h": len(hull)}


# ===== ГЕОМЕТРИЯ =====

def perimeter(hull):
    """Периметр многоугольника."""
    if len(hull) < 2:
        return 0.0
    total = 0.0
    for i in range(len(hull)):
        j = (i + 1) % len(hull)
        total += math.sqrt(dist_sq(hull[i], hull[j]))
    return total


def area(hull):
    """Площадь по формуле шнурков (Shoelace)."""
    if len(hull) < 3:
        return 0.0
    s = 0.0
    n = len(hull)
    for i in range(n):
        j = (i + 1) % n
        s += hull[i].x * hull[j].y
        s -= hull[j].x * hull[i].y
    return abs(s) / 2.0


# ===== РАБОТА С ФАЙЛАМИ =====

def load_points(filepath):
    """Загружает точки из файла (txt/csv/json)."""
    points = []
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.json':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                points.append(Point(item['x'], item['y']))

    elif ext == '.csv':
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                points.append(Point(float(row['x']), float(row['y'])))

    elif ext == '.txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.replace(',', ' ').split()
                if len(parts) >= 2:
                    points.append(Point(float(parts[0]), float(parts[1])))

    return points


def save_points(filepath, points):
    """Сохраняет точки в файл."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.json':
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([{'x': p.x, 'y': p.y} for p in points], f, indent=2)

    elif ext == '.csv':
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['x', 'y'])
            writer.writeheader()
            for p in points:
                writer.writerow({'x': p.x, 'y': p.y})

    elif ext == '.txt':
        with open(filepath, 'w', encoding='utf-8') as f:
            for p in points:
                f.write(f"{p.x} {p.y}\n")


# ===== ГРАФИЧЕСКИЙ ИНТЕРФЕЙС =====

class HullApp:
    """Главное окно приложения."""

    def __init__(self, root):
        self.root = root
        self.root.title("Выпуклая оболочка — вариант А-24 (Медведев Д.В., БИН-24-1)")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Текущие точки
        self.points = []
        self.hull = []
        self.highlight = []
        self.status_text = "Добавьте точки кликом по холсту или загрузите из файла"

        # Масштаб отображения
        self.canvas_w = 800
        self.canvas_h = 600
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self._build_ui()
        self._draw()

    def _build_ui(self):
        """Создаём интерфейс."""

        # === Верхняя панель кнопок ===
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="➕ Добавить точку", command=self._add_random).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="📂 Загрузить файл", command=self._load_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="💾 Сохранить точки", command=self._save_file).pack(side=tk.LEFT, padx=3)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(toolbar, text="▶ Грэхем", command=lambda: self._run_algorithm('graham')).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="▶ Джарвис", command=lambda: self._run_algorithm('jarvis')).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="⚔ Сравнить оба", command=self._compare).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🎞 Анимация (Грэхем)", command=lambda: self._run_animated('graham')).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🎞 Анимация (Джарвис)", command=lambda: self._run_animated('jarvis')).pack(side=tk.LEFT, padx=3)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(toolbar, text="🧹 Очистить", command=self._clear).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="📐 Пример данных", command=self._load_sample).pack(side=tk.LEFT, padx=3)

        # === Основная область: холст + панель справа ===
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Холст
        self.canvas = tk.Canvas(main_frame, bg="white", highlightthickness=1, highlightbackground="#888")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", self._on_resize)

        # Правая панель с информацией
        info_frame = ttk.Frame(main_frame, width=280, padding=5)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        info_frame.pack_propagate(False)

        ttk.Label(info_frame, text="📊 Информация", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)

        self.info_text = tk.Text(info_frame, width=35, height=30, font=("Consolas", 10))
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(info_frame, text="💡 Подсказка:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        hint = ("• Клик по холсту — добавить точку\n"
                "• Кнопки сверху — запуск алгоритмов\n"
                "• Анимация — пошаговое построение\n"
                "• Поддерживаются: .txt, .csv, .json")
        ttk.Label(info_frame, text=hint, foreground="#555").pack(anchor=tk.W)

        # === Нижняя строка состояния ===
        status_frame = ttk.Frame(self.root, padding=3)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text=self.status_text, foreground="#333")
        self.status_label.pack(anchor=tk.W)

    def _on_resize(self, event):
        self.canvas_w = event.width
        self.canvas_h = event.height
        self._draw()

    def _world_to_screen(self, p):
        """Преобразование мировых координат в экранные."""
        if not self.points:
            return p.x, p.y

        # Вычисляем границы
        xs = [pt.x for pt in self.points]
        ys = [pt.y for pt in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Добавляем отступы
        w = max_x - min_x if max_x > min_x else 10
        h = max_y - min_y if max_y > min_y else 10
        min_x -= w * 0.1
        min_y -= h * 0.1
        w *= 1.2
        h *= 1.2

        # Масштабируем с сохранением пропорций
        sx = self.canvas_w / w
        sy = self.canvas_h / h
        s = min(sx, sy)

        # Центрируем
        cx = (self.canvas_w - w * s) / 2
        cy = (self.canvas_h - h * s) / 2

        # Инвертируем Y (на экране Y растёт вниз)
        screen_x = (p.x - min_x) * s + cx
        screen_y = self.canvas_h - ((p.y - min_y) * s + cy)
        return screen_x, screen_y

    def _screen_to_world(self, sx, sy):
        """Обратное преобразование."""
        if not self.points:
            return sx, self.canvas_h - sy

        xs = [pt.x for pt in self.points]
        ys = [pt.y for pt in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        w = max_x - min_x if max_x > min_x else 10
        h = max_y - min_y if max_y > min_y else 10
        min_x -= w * 0.1
        min_y -= h * 0.1
        w *= 1.2
        h *= 1.2

        sx_s = self.canvas_w / w
        sy_s = self.canvas_h / h
        s = min(sx_s, sy_s)

        cx = (self.canvas_w - w * s) / 2
        cy = (self.canvas_h - h * s) / 2

        x = (sx - cx) / s + min_x
        y = (self.canvas_h - sy - cy) / s + min_y
        return x, y

    def _on_click(self, event):
        """Клик по холсту — добавляем точку."""
        x, y = self._screen_to_world(event.x, event.y)
        # Округляем для красоты
        x, y = round(x, 1), round(y, 1)
        self.points.append(Point(x, y))
        self._draw()
        self.status_label.config(text=f"Добавлена точка ({x}, {y}). Всего точек: {len(self.points)}")

    def _add_random(self):
        """Добавить случайную точку."""
        import random
        x = round(random.uniform(0, 100), 1)
        y = round(random.uniform(0, 100), 1)
        self.points.append(Point(x, y))
        self._draw()

    def _load_sample(self):
        """Загрузить пример."""
        sample = [
            (10, 20), (30, 80), (50, 30), (70, 90), (90, 20),
            (20, 50), (40, 40), (60, 60), (80, 50), (50, 50),
            (25, 75), (75, 75), (15, 35), (85, 65)
        ]
        self.points = [Point(x, y) for x, y in sample]
        self._draw()
        self.status_label.config(text="Загружены примерные данные")

    def _load_file(self):
        """Загрузить точки из файла."""
        filepath = filedialog.askopenfilename(
            title="Выберите файл с точками",
            filetypes=[
                ("Все поддерживаемые", "*.txt *.csv *.json"),
                ("JSON", "*.json"),
                ("CSV", "*.csv"),
                ("Текст", "*.txt"),
            ]
        )
        if not filepath:
            return
        try:
            self.points = load_points(filepath)
            self._draw()
            self.status_label.config(text=f"Загружено {len(self.points)} точек из {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def _save_file(self):
        """Сохранить точки."""
        if not self.points:
            messagebox.showwarning("Внимание", "Нет точек для сохранения")
            return
        filepath = filedialog.asksaveasfilename(
            title="Сохранить точки",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("CSV", "*.csv"), ("Текст", "*.txt")]
        )
        if not filepath:
            return
        try:
            save_points(filepath, self.points)
            self.status_label.config(text=f"Сохранено в {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def _clear(self):
        """Очистить всё."""
        self.points = []
        self.hull = []
        self.highlight = []
        self.info_text.delete("1.0", tk.END)
        self._draw()
        self.status_label.config(text="Холст очищен")

    def _draw(self):
        """Отрисовка всего на холсте."""
        self.canvas.delete("all")

        # Координатная сетка (опционально)
        for i in range(0, 1100, 50):
            self.canvas.create_line(i, 0, i, 800, fill="#f0f0f0", width=1)
            self.canvas.create_line(0, i, 1100, i, fill="#f0f0f0", width=1)

        if not self.points:
            self.canvas.create_text(
                self.canvas_w // 2, self.canvas_h // 2,
                text="Кликните здесь, чтобы добавить точку",
                font=("Arial", 14), fill="#999"
            )
            return

        # Отрисовка оболочки
        if len(self.hull) >= 2:
            screen_pts = [self._world_to_screen(p) for p in self.hull]
            # Заливка
            flat = [c for pt in screen_pts for c in pt]
            if len(flat) >= 6:
                self.canvas.create_polygon(flat, fill="#b3d9ff", outline="", stipple="gray25")
            # Контур
            for i in range(len(screen_pts)):
                j = (i + 1) % len(screen_pts)
                self.canvas.create_line(
                    screen_pts[i][0], screen_pts[i][1],
                    screen_pts[j][0], screen_pts[j][1],
                    fill="#0066cc", width=2
                )

        # Отрисовка всех точек
        for p in self.points:
            sx, sy = self._world_to_screen(p)
            color = "gray"
            size = 4
            # Если точка в оболочке — синяя
            if self.hull and any(abs(p.x - h.x) < 1e-6 and abs(p.y - h.y) < 1e-6 for h in self.hull):
                color = "#0066cc"
                size = 6
            # Если точка подсвечена — красная
            if any(abs(p.x - h.x) < 1e-6 and abs(p.y - h.y) < 1e-6 for h in self.highlight):
                color = "red"
                size = 8

            self.canvas.create_oval(
                sx - size, sy - size, sx + size, sy + size,
                fill=color, outline="black"
            )
            # Подпись координат
            self.canvas.create_text(
                sx + 8, sy - 8,
                text=f"({p.x:.0f},{p.y:.0f})",
                font=("Consolas", 8), fill="#555", anchor=tk.NW
            )

    def _run_algorithm(self, algo_name):
        """Запуск алгоритма (без анимации)."""
        if len(self.points) < 3:
            messagebox.showwarning("Мало точек", "Нужно минимум 3 точки для построения оболочки")
            return

        self.highlight = []
        start_time = time.time()

        if algo_name == 'graham':
            hull, stats = ConvexHull.graham_scan(self.points)
            name = "Сканирование Грэхема"
        else:
            hull, stats = ConvexHull.jarvis_march(self.points)
            name = "Обход Джарвиса"

        elapsed = time.time() - start_time
        self.hull = hull
        self._draw()

        perim = perimeter(hull)
        ar = area(hull)

        report = (
            f"=== {name} ===\n\n"
            f"Точек на входе: {len(self.points)}\n"
            f"Вершин оболочки: {stats['h']}\n"
            f"Операций выполнено: {stats['ops']}\n"
            f"Время: {elapsed*1000:.2f} мс\n\n"
            f"Периметр: {perim:.2f}\n"
            f"Площадь: {ar:.2f}\n\n"
            f"Вершины оболочки:\n"
        )
        for i, p in enumerate(hull, 1):
            report += f"  {i}. ({p.x:.1f}, {p.y:.1f})\n"

        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, report)
        self.status_label.config(text=f"{name}: готово")

    def _compare(self):
        """Сравнить оба алгоритма."""
        if len(self.points) < 3:
            messagebox.showwarning("Мало точек", "Нужно минимум 3 точки")
            return

        h1, s1 = ConvexHull.graham_scan(self.points)
        h2, s2 = ConvexHull.jarvis_march(self.points)

        self.hull = h1
        self._draw()

        report = (
            "=== СРАВНЕНИЕ АЛГОРИТМОВ ===\n\n"
            f"Точек: {len(self.points)}\n"
            f"Вершин оболочки: {s1['h']}\n\n"
            f"─── Грэхем ───\n"
            f"  Операций: {s1['ops']}\n"
            f"  Сложность: O(n log n)\n\n"
            f"─── Джарвис ───\n"
            f"  Операций: {s2['ops']}\n"
            f"  Сложность: O(n·h)\n\n"
            f"─── Результат ───\n"
            f"Периметр: {perimeter(h1):.2f}\n"
            f"Площадь: {area(h1):.2f}\n\n"
        )

        if s1['ops'] < s2['ops']:
            winner = "🏆 Грэхем быстрее"
        elif s2['ops'] < s1['ops']:
            winner = "🏆 Джарвис быстрее"
        else:
            winner = "🤝 Ничья"
        report += "Вывод:\n"
        report += "  Грэхем эффективнее, когда h велико (сравнимо с n).\n"
        report += "  Джарвис выгоден, когда h очень мало (h << log n).\n"
        report += "  При большом n и малом h — Джарвис может быть быстрее.\n"
        report += "  При большом n и большом h — Грэхем однозначно лучше."
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, report)
        self.status_label.config(text="Сравнение выполнено")

    def _run_animated(self, algo_name):
        """Пошаговая анимация алгоритма."""
        if len(self.points) < 3:
            messagebox.showwarning("Мало точек", "Нужно минимум 3 точки")
            return

        self.status_label.config(text=f"Анимация: {algo_name}...")

        steps = []

        def collect(description, points, hull, highlight, ops):
            steps.append({
                'desc': description,
                'hull': list(hull),
                'highlight': list(highlight),
                'ops': ops
            })

        if algo_name == 'graham':
            hull, stats = ConvexHull.graham_scan(self.points, on_step=collect)
        else:
            hull, stats = ConvexHull.jarvis_march(self.points, on_step=collect)

        self.hull = hull
        self._draw()

        # Запускаем анимацию в отдельном потоке, чтобы не блокировать интерфейс
        def animate():
            for step in steps:
                self.hull = step['hull']
                self.highlight = step['highlight']
                self.root.after(0, self._draw)
                self.root.after(0, lambda d=step['desc'], o=step['ops']:
                    self.status_label.config(text=f"[оп. {o}] {d}"))
                time.sleep(0.4)  # пауза между шагами
            self.root.after(0, lambda: self.status_label.config(
                text=f"Анимация завершена. Вершин: {stats['h']}, Операций: {stats['ops']}"))

        threading.Thread(target=animate, daemon=True).start()


def main():
    root = tk.Tk()
    # Пытаемся задать иконку (если есть)
    try:
        root.iconbitmap(default='icon.ico')
    except Exception:
        pass
    app = HullApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()