import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import numpy as np


class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def rotate_x(self, angle):
        y = self.y * math.cos(angle) - self.z * math.sin(angle)
        z = self.y * math.sin(angle) + self.z * math.cos(angle)
        return Point3D(self.x, y, z)

    def rotate_y(self, angle):
        x = self.x * math.cos(angle) + self.z * math.sin(angle)
        z = -self.x * math.sin(angle) + self.z * math.cos(angle)
        return Point3D(x, self.y, z)

    def rotate_z(self, angle):
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Point3D(x, y, self.z)

    def project(self, canvas_width, canvas_height, scale, offset_x, offset_y):
        perspective = 1 + self.z * 0.1
        x_proj = self.x * scale * perspective + offset_x
        y_proj = -self.y * scale * perspective + offset_y
        return x_proj, y_proj


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Построение кривых и поверхностей - 3D")
        self.root.geometry("1300x800")

        self.canvas_width = 900
        self.canvas_height = 700
        self.scale = 50
        self.offset_x = self.canvas_width // 2
        self.offset_y = self.canvas_height // 2

        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

        self.current_method = "bezier_quad"
        self.control_points = []
        self.subdivisions = 3
        self.t_parameter = 0.5
        self.step_mode = False
        self.current_step = 0

        self.examples = {
            "bezier_quad": [
                Point3D(-4, 2, 1),
                Point3D(0, 4, 2),
                Point3D(4, 2, 1),
                Point3D(6, -1, 0),
                Point3D(4, -3, -1),
                Point3D(0, -2, 0),
                Point3D(-4, -3, -1),
                Point3D(-6, -1, 0)
            ],
            "bezier_cubic": [
                Point3D(-5, 0, 1),
                Point3D(-3, 4, 3),
                Point3D(0, 4, 2),
                Point3D(3, 0, 1),
                Point3D(3, -3, 0),
                Point3D(0, -5, -1),
                Point3D(-3, -3, 0),
                Point3D(-5, 0, 1)
            ],
            "chaikin": [
                Point3D(-5, -3, 0),
                Point3D(-2, 4, 2),
                Point3D(0, 1, 1),
                Point3D(3, 5, 3),
                Point3D(5, -2, 0),
                Point3D(2, -4, -2),
                Point3D(-1, -1, -1)
            ],
            "bezier_surface": [
                Point3D(-3, -3, 2), Point3D(-1, -3, 1), Point3D(1, -3, 0), Point3D(3, -3, 1),
                Point3D(-3, -1, 1), Point3D(-1, -1, 3), Point3D(1, -1, 2), Point3D(3, -1, 0),
                Point3D(-3, 1, 0), Point3D(-1, 1, 2), Point3D(1, 1, 3), Point3D(3, 1, 1),
                Point3D(-3, 3, 1), Point3D(-1, 3, 0), Point3D(1, 3, 1), Point3D(3, 3, 2)
            ],
            "doo_sabin": [
                Point3D(-3, 0, 0),
                Point3D(-1, 3, 2),
                Point3D(1, 3, 1),
                Point3D(3, 0, 0),
                Point3D(1, -3, 2),
                Point3D(-1, -3, 1),
                Point3D(-2, -1, 3),
                Point3D(2, -1, -1)
            ]
        }

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Method.TRadiobutton', font=('Arial', 10))
        style.configure('Control.TButton', font=('Arial', 10))
        style.configure('Example.TButton', font=('Arial', 10, 'bold'), foreground='white', background='#4CAF50')
        style.map('Example.TButton', background=[('active', '#45a049')])

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.LabelFrame(main_frame, text="Управление", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_control_panel(left_frame)
        self.setup_canvas(right_frame)
        self.setup_points_table(left_frame)

    def setup_control_panel(self, parent):
        ttk.Label(parent, text="Выбор метода:", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))

        methods = [
            ("Квадратичная кривая Безье", "bezier_quad"),
            ("Кубическая кривая Безье", "bezier_cubic"),
            ("Кривая Чайкина", "chaikin"),
            ("Поверхность Безье", "bezier_surface"),
            ("Поверхность Ду-Сабина", "doo_sabin")
        ]

        self.method_var = tk.StringVar(value=self.current_method)
        for text, method in methods:
            rb = ttk.Radiobutton(parent, text=text, variable=self.method_var,
                                 value=method, command=self.change_method)
            rb.pack(anchor=tk.W, pady=2)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(parent, text="Вращение 3D:", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(parent, text="Вращение X:").pack(anchor=tk.W)
        self.rotate_x_slider = tk.Scale(parent, from_=0, to=360, orient=tk.HORIZONTAL,
                                        length=200, command=self.update_rotation)
        self.rotate_x_slider.set(0)
        self.rotate_x_slider.pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(parent, text="Вращение Y:").pack(anchor=tk.W)
        self.rotate_y_slider = tk.Scale(parent, from_=0, to=360, orient=tk.HORIZONTAL,
                                        length=200, command=self.update_rotation)
        self.rotate_y_slider.set(0)
        self.rotate_y_slider.pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(parent, text="Вращение Z:").pack(anchor=tk.W)
        self.rotate_z_slider = tk.Scale(parent, from_=0, to=360, orient=tk.HORIZONTAL,
                                        length=200, command=self.update_rotation)
        self.rotate_z_slider.set(0)
        self.rotate_z_slider.pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(parent, text="Параметры построения:", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(parent, text="Разбиений:").pack(anchor=tk.W)
        self.subdiv_slider = tk.Scale(parent, from_=1, to=10, orient=tk.HORIZONTAL,
                                      length=200, command=self.update_subdivisions)
        self.subdiv_slider.set(self.subdivisions)
        self.subdiv_slider.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(parent, text="Параметр t (0-1):").pack(anchor=tk.W)
        self.t_slider = tk.Scale(parent, from_=0, to=100, orient=tk.HORIZONTAL,
                                 length=200, command=self.update_t_parameter)
        self.t_slider.set(50)
        self.t_slider.pack(anchor=tk.W, pady=(0, 10))

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Добавить точку", command=self.add_random_point,
                   style='Control.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Очистить", command=self.clear,
                   style='Control.TButton').pack(side=tk.LEFT, padx=2)

        btn_frame2 = ttk.Frame(parent)
        btn_frame2.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame2, text="Построить", command=self.draw,
                   style='Control.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame2, text="Шаг", command=self.step_build,
                   style='Control.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame2, text="Сохранить в OBJ", command=self.save_to_obj,
                   style='Control.TButton').pack(side=tk.LEFT, padx=2)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Button(parent, text="Загрузить пример", command=self.load_example,
                   style='Example.TButton').pack(fill=tk.X, pady=5)

        self.step_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Пошаговый режим", variable=self.step_var,
                        command=self.toggle_step_mode).pack(anchor=tk.W, pady=5)

        self.info_label = ttk.Label(parent, text="Точек: 0", font=('Arial', 10))
        self.info_label.pack(anchor=tk.W, pady=10)

    def setup_points_table(self, parent):
        frame = ttk.LabelFrame(parent, text="Точки управления (x, y, z)", padding=5)
        frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        canvas = tk.Canvas(frame, height=150)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.points_frame = scrollable_frame
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_canvas(self, parent):
        canvas_frame = ttk.LabelFrame(parent, text="3D Визуализация", padding=10)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width,
                                height=self.canvas_height, bg="white", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<MouseWheel>", self.zoom)

        self.draw_grid()

    def update_rotation(self, value=None):
        self.angle_x = math.radians(self.rotate_x_slider.get())
        self.angle_y = math.radians(self.rotate_y_slider.get())
        self.angle_z = math.radians(self.rotate_z_slider.get())
        self.draw()

    def zoom(self, event):
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale *= 0.9
        self.draw()

    def save_to_obj(self):
        if not self.control_points:
            messagebox.showwarning("Внимание", "Нет данных для сохранения!")
            return

        geometry_data = self.get_current_geometry()

        if not geometry_data:
            messagebox.showwarning("Внимание", "Не удалось получить геометрию для сохранения!")
            return

        vertices, elements = geometry_data
        element_type = 'l' if 'curve' in self.current_method else 'f'

        filename = filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("OBJ файлы", "*.obj"), ("Все файлы", "*.*")],
            title="Сохранить 3D геометрию как..."
        )

        if not filename:
            return

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# 3D геометрия\n")
                f.write(f"# Метод: {self.current_method}\n")
                f.write(f"# Разбиений: {self.subdivisions}, Параметр t: {self.t_parameter}\n")
                f.write(f"# Вершин: {len(vertices)}, Элементов: {len(elements)}\n\n")

                method_names = {
                    "bezier_quad": "QuadraticBezierCurve3D",
                    "bezier_cubic": "CubicBezierCurve3D",
                    "chaikin": "ChaikinCurve3D",
                    "bezier_surface": "BezierSurface3D",
                    "doo_sabin": "DooSabinSurface3D"
                }
                obj_name = method_names.get(self.current_method, "Geometry3D")
                f.write(f"o {obj_name}\n\n")

                for vertex in vertices:
                    x, y, z = vertex
                    f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")

                f.write("\n")

                if element_type == 'l':
                    indices = [str(i + 1) for i in range(len(vertices))]
                    f.write(f"l {' '.join(indices)}\n")
                else:
                    for element in elements:
                        indices = [str(idx + 1) for idx in element]
                        f.write(f"f {' '.join(indices)}\n")

            messagebox.showinfo("Успех", f"3D геометрия сохранена в файл:\n{filename}")
            print(f"✓ Файл '{filename}' успешно сохранен!")
            print(f"  Метод: {self.current_method}")
            print(f"  Вершин: {len(vertices)}")
            print(f"  Элементов: {len(elements)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении файла:\n{str(e)}")

    def get_current_geometry(self):
        if self.current_method == "bezier_quad" and len(self.control_points) >= 3:
            return self.get_bezier_quad_geometry()
        elif self.current_method == "bezier_cubic" and len(self.control_points) >= 4:
            return self.get_bezier_cubic_geometry()
        elif self.current_method == "chaikin" and len(self.control_points) >= 2:
            return self.get_chaikin_geometry()
        elif self.current_method == "bezier_surface" and len(self.control_points) >= 4:
            return self.get_bezier_surface_geometry()
        elif self.current_method == "doo_sabin" and len(self.control_points) >= 3:
            return self.get_doo_sabin_geometry()

        return None

    def get_bezier_quad_geometry(self):
        steps = 50
        curve_points = []
        for t in [i / steps for i in range(steps + 1)]:
            curve_points.extend(self.bezier_quad(self.control_points, t))

        vertices = [(p.x, p.y, p.z) for p in curve_points]
        elements = [list(range(len(vertices)))]
        return vertices, elements

    def get_bezier_cubic_geometry(self):
        steps = 50
        curve_points = []
        for t in [i / steps for i in range(steps + 1)]:
            curve_points.extend(self.bezier_cubic(self.control_points, t))

        vertices = [(p.x, p.y, p.z) for p in curve_points]
        elements = [list(range(len(vertices)))]
        return vertices, elements

    def get_chaikin_geometry(self):
        chaikin_points = self.chaikin(self.control_points, self.subdivisions)
        vertices = [(p.x, p.y, p.z) for p in chaikin_points]
        elements = [list(range(len(vertices)))]
        return vertices, elements

    def get_bezier_surface_geometry(self):
        surface_grid = self.bezier_surface(self.control_points, self.subdivisions)
        if not surface_grid:
            return None

        vertices = []
        for row in surface_grid:
            for p in row:
                vertices.append((p.x, p.y, p.z))

        n = len(surface_grid)
        elements = []

        for i in range(n - 1):
            for j in range(n - 1):
                v1 = i * n + j
                v2 = i * n + (j + 1)
                v3 = (i + 1) * n + j
                v4 = (i + 1) * n + (j + 1)

                elements.append([v1, v2, v3])
                elements.append([v2, v4, v3])

        return vertices, elements

    def get_doo_sabin_geometry(self):
        doo_points = self.doo_sabin(self.control_points, self.subdivisions)
        if not doo_points:
            return None

        vertices = [(p.x, p.y, p.z) for p in doo_points]
        elements = [list(range(len(vertices)))]
        return vertices, elements

    def load_example(self):
        if self.current_method in self.examples:
            self.control_points = [Point3D(p.x, p.y, p.z) for p in self.examples[self.current_method]]
            self.update_points_list()
            self.draw()

            if self.current_method in ["bezier_quad", "bezier_cubic"]:
                self.t_slider.set(50)
            elif self.current_method in ["chaikin", "doo_sabin"]:
                self.subdiv_slider.set(5)
            elif self.current_method == "bezier_surface":
                self.subdiv_slider.set(4)

    def draw_grid(self):
        self.canvas.delete("grid")

        for i in range(-10, 11):
            x = i * self.scale + self.offset_x
            self.canvas.create_line(x, self.offset_y - 3, x, self.offset_y + 3, fill="red", width=1, tags="grid")

        for i in range(-10, 11):
            y = i * self.scale + self.offset_y
            self.canvas.create_line(self.offset_x - 3, y, self.offset_x + 3, y, fill="green", width=1, tags="grid")

        for i in range(-10, 11):
            z = i * 0.5
            x1 = self.offset_x - z * self.scale * 0.7
            y1 = self.offset_y - z * self.scale * 0.7
            x2 = self.offset_x + z * self.scale * 0.7
            y2 = self.offset_y + z * self.scale * 0.7
            self.canvas.create_oval(x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill="blue", outline="", tags="grid")

    def change_method(self):
        self.current_method = self.method_var.get()
        self.current_step = 0
        self.draw()

    def update_subdivisions(self, value):
        self.subdivisions = int(value)
        if not self.step_mode:
            self.draw()

    def update_t_parameter(self, value):
        self.t_parameter = int(value) / 100.0
        if not self.step_mode:
            self.draw()

    def add_random_point(self):
        import random
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        z = random.uniform(-3, 3)
        self.control_points.append(Point3D(x, y, z))
        self.update_points_list()
        self.draw()

    def rotate_point_for_display(self, point):
        rotated = point.rotate_x(self.angle_x)
        rotated = rotated.rotate_y(self.angle_y)
        rotated = rotated.rotate_z(self.angle_z)
        return rotated

    def project_point(self, point):
        rotated = self.rotate_point_for_display(point)
        return rotated.project(self.canvas_width, self.canvas_height, self.scale, self.offset_x, self.offset_y)

    def canvas_click(self, event):
        x = (event.x - self.offset_x) / self.scale
        y = -(event.y - self.offset_y) / self.scale

        z = 0
        if "surface" in self.current_method:
            z = (len(self.control_points) % 6) - 3

        if event.state & 0x0004:
            if self.control_points:
                min_dist = float('inf')
                closest_idx = -1
                for i, p in enumerate(self.control_points):
                    px, py = self.project_point(p)
                    dist = math.sqrt((px - event.x) ** 2 + (py - event.y) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = i
                if min_dist < 10:
                    del self.control_points[closest_idx]
                    self.update_points_list()
        else:
            self.control_points.append(Point3D(x, y, z))
            self.update_points_list()

        self.draw()

    def canvas_drag(self, event):
        if not self.control_points:
            return

        min_dist = float('inf')
        closest_idx = -1
        for i, p in enumerate(self.control_points):
            px, py = self.project_point(p)
            dist = math.sqrt((px - event.x) ** 2 + (py - event.y) ** 2)
            if dist < min_dist and dist < 15:
                min_dist = dist
                closest_idx = i

        if closest_idx >= 0:
            if event.state & 0x0001:
                delta_z = (event.y - self.last_drag_y) / 50.0
                self.control_points[closest_idx].z += delta_z
            else:
                x = (event.x - self.offset_x) / self.scale
                y = -(event.y - self.offset_y) / self.scale
                self.control_points[closest_idx].x = x
                self.control_points[closest_idx].y = y

            self.update_points_list()
            self.draw()

        self.last_drag_y = event.y

    def update_points_list(self):
        for widget in self.points_frame.winfo_children():
            widget.destroy()

        for i, point in enumerate(self.control_points):
            frame = ttk.Frame(self.points_frame)
            frame.pack(fill=tk.X, pady=1)

            ttk.Label(frame, text=f"{i}:", width=4).pack(side=tk.LEFT)
            ttk.Label(frame, text=f"({point.x:.2f}, {point.y:.2f}, {point.z:.2f})", width=25).pack(side=tk.LEFT)

            btn = ttk.Button(frame, text="✕", width=3,
                             command=lambda idx=i: self.delete_point(idx))
            btn.pack(side=tk.RIGHT)

        self.info_label.config(text=f"Точек: {len(self.control_points)}")

    def delete_point(self, index):
        if 0 <= index < len(self.control_points):
            del self.control_points[index]
            self.update_points_list()
            self.draw()

    def clear(self):
        self.control_points.clear()
        self.update_points_list()
        self.current_step = 0
        self.canvas.delete("all")
        self.draw_grid()

    def bernstein(self, i, n, t):
        from math import comb
        return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def bezier_quad(self, points, t):
        result = []
        if len(points) < 3:
            return result

        for seg in range(0, len(points) - 2, 2):
            if seg + 2 >= len(points):
                break
            p0, p1, p2 = points[seg], points[seg + 1], points[seg + 2]
            x = (1 - t) ** 2 * p0.x + 2 * (1 - t) * t * p1.x + t ** 2 * p2.x
            y = (1 - t) ** 2 * p0.y + 2 * (1 - t) * t * p1.y + t ** 2 * p2.y
            z = (1 - t) ** 2 * p0.z + 2 * (1 - t) * t * p1.z + t ** 2 * p2.z
            result.append(Point3D(x, y, z))

        return result

    def bezier_cubic(self, points, t):
        result = []
        if len(points) < 4:
            return result

        for seg in range(0, len(points) - 3, 3):
            if seg + 3 >= len(points):
                break
            p0, p1, p2, p3 = points[seg], points[seg + 1], points[seg + 2], points[seg + 3]
            x = (1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t ** 2 * p2.x + t ** 3 * p3.x
            y = (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t ** 2 * p2.y + t ** 3 * p3.y
            z = (1 - t) ** 3 * p0.z + 3 * (1 - t) ** 2 * t * p1.z + 3 * (1 - t) * t ** 2 * p2.z + t ** 3 * p3.z
            result.append(Point3D(x, y, z))

        return result

    def chaikin(self, points, iterations):
        if len(points) < 2:
            return points

        current = points.copy()

        for iter_num in range(min(iterations, self.subdivisions)):
            if self.step_mode and iter_num >= self.current_step:
                break

            new_points = []
            for i in range(len(current) - 1):
                p0 = current[i]
                p1 = current[i + 1]
                q = Point3D(0.75 * p0.x + 0.25 * p1.x, 0.75 * p0.y + 0.25 * p1.y, 0.75 * p0.z + 0.25 * p1.z)
                r = Point3D(0.25 * p0.x + 0.75 * p1.x, 0.25 * p0.y + 0.75 * p1.y, 0.25 * p0.z + 0.75 * p1.z)
                new_points.extend([q, r])
            current = new_points

        return current

    def bezier_surface(self, points, subdivisions):
        if len(points) < 4:
            return []

        n = int(math.sqrt(len(points)))
        if n < 2:
            n = 2
        if n * n > len(points):
            n = int(math.sqrt(len(points)))

        surface = []
        steps = subdivisions + 2

        for i in range(steps):
            u = i / (steps - 1) if steps > 1 else 0
            row = []
            for j in range(steps):
                v = j / (steps - 1) if steps > 1 else 0
                sum_x = sum_y = sum_z = 0
                for ii in range(n):
                    for jj in range(n):
                        idx = ii * n + jj
                        if idx < len(points):
                            basis = self.bernstein(ii, n - 1, u) * self.bernstein(jj, n - 1, v)
                            sum_x += points[idx].x * basis
                            sum_y += points[idx].y * basis
                            sum_z += points[idx].z * basis
                row.append(Point3D(sum_x, sum_y, sum_z))
            surface.append(row)

        return surface

    def doo_sabin(self, points, iterations):
        if len(points) < 3:
            return []

        current = points.copy()

        for iter_num in range(min(iterations, self.subdivisions)):
            if self.step_mode and iter_num >= self.current_step:
                break

            new_points = []
            n = len(current)

            for i in range(n):
                p0 = current[i]
                p1 = current[(i + 1) % n]
                p2 = current[(i + 2) % n]

                face_center = Point3D((p0.x + p1.x + p2.x) / 3, (p0.y + p1.y + p2.y) / 3, (p0.z + p1.z + p2.z) / 3)
                edge1_mid = Point3D((p0.x + p1.x) / 2, (p0.y + p1.y) / 2, (p0.z + p1.z) / 2)
                edge2_mid = Point3D((p1.x + p2.x) / 2, (p1.y + p2.y) / 2, (p1.z + p2.z) / 2)

                new_point = Point3D(
                    (p0.x + edge1_mid.x + edge2_mid.x + face_center.x) / 4,
                    (p0.y + edge1_mid.y + edge2_mid.y + face_center.y) / 4,
                    (p0.z + edge1_mid.z + edge2_mid.z + face_center.z) / 4
                )
                new_points.append(new_point)

            current = new_points

        return current

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()

        for i, point in enumerate(self.control_points):
            x, y = self.project_point(point)
            z_normalized = (point.z + 5) / 10
            color = self.get_color_by_z(z_normalized)

            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="black", width=2, tags="points")
            self.canvas.create_text(x + 10, y - 10, text=str(i), fill="black", font=("Arial", 9), tags="points")

        if len(self.control_points) > 1:
            points_proj = [self.project_point(p) for p in self.control_points]
            for i in range(len(points_proj) - 1):
                x1, y1 = points_proj[i]
                x2, y2 = points_proj[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="#888", dash=(3, 2), width=1, tags="polygon")

        if self.current_method == "bezier_quad" and len(self.control_points) >= 3:
            curve_points = []
            steps = 50 if not self.step_mode else min(50, (self.current_step + 1) * 10)
            for t in [i / steps for i in range(steps + 1)]:
                curve_points.extend(self.bezier_quad(self.control_points, t))
            self.draw_curve(curve_points, "#0066cc")

        elif self.current_method == "bezier_cubic" and len(self.control_points) >= 4:
            curve_points = []
            steps = 50 if not self.step_mode else min(50, (self.current_step + 1) * 10)
            for t in [i / steps for i in range(steps + 1)]:
                curve_points.extend(self.bezier_cubic(self.control_points, t))
            self.draw_curve(curve_points, "#00aa44")

        elif self.current_method == "chaikin" and len(self.control_points) >= 2:
            chaikin_points = self.chaikin(self.control_points, self.subdivisions)
            self.draw_curve(chaikin_points, "#aa44aa", len(self.control_points) > 2)

        elif self.current_method == "bezier_surface" and len(self.control_points) >= 4:
            surface_grid = self.bezier_surface(self.control_points, self.subdivisions)
            if surface_grid:
                self.draw_surface(surface_grid, "#ff8800")

        elif self.current_method == "doo_sabin" and len(self.control_points) >= 3:
            doo_points = self.doo_sabin(self.control_points, self.subdivisions)
            if doo_points:
                self.draw_curve(doo_points, "#880000", True)

    def get_color_by_z(self, z):
        if z < 0.33:
            r = int(255 * (z * 3))
            g = int(255 * (z * 3))
            b = 255
        elif z < 0.66:
            r = 0
            g = 255
            b = int(255 * (1 - (z - 0.33) * 3))
        else:
            r = 255
            g = int(255 * (1 - (z - 0.66) * 3))
            b = 0

        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_curve(self, points, color, close=False):
        if len(points) < 2:
            return

        for i in range(len(points) - 1):
            x1, y1 = self.project_point(points[i])
            x2, y2 = self.project_point(points[i + 1])

            z_avg = (points[i].z + points[i + 1].z) / 2
            thickness = max(1, min(4, int(2 + z_avg)))

            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, tags="curve")

        if close and len(points) > 2:
            x1, y1 = self.project_point(points[-1])
            x2, y2 = self.project_point(points[0])
            z_avg = (points[-1].z + points[0].z) / 2
            thickness = max(1, min(4, int(2 + z_avg)))
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, tags="curve")

    def draw_surface(self, grid, color):
        if not grid or len(grid) < 2:
            return

        n = len(grid)

        for i in range(n):
            for j in range(n - 1):
                x1, y1 = self.project_point(grid[i][j])
                x2, y2 = self.project_point(grid[i][j + 1])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, tags="surface")

        for j in range(n):
            for i in range(n - 1):
                x1, y1 = self.project_point(grid[i][j])
                x2, y2 = self.project_point(grid[i + 1][j])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, tags="surface")

        for i in range(n):
            for j in range(n):
                x, y = self.project_point(grid[i][j])
                z_color = self.get_color_by_z((grid[i][j].z + 3) / 6)
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=z_color, outline="black", width=1,
                                        tags="surface")

    def toggle_step_mode(self):
        self.step_mode = self.step_var.get()
        self.current_step = 0
        if self.step_mode:
            self.info_label.config(text=f"Точек: {len(self.control_points)} (Шаг: {self.current_step})")
        else:
            self.info_label.config(text=f"Точек: {len(self.control_points)}")
        self.draw()

    def step_build(self):
        if self.step_mode:
            self.current_step += 1
            self.info_label.config(text=f"Точек: {len(self.control_points)} (Шаг: {self.current_step})")
            self.draw()
        elif self.current_method in ["bezier_quad", "bezier_cubic"]:
            self.t_slider.set((self.t_slider.get() + 5) % 105)
        else:
            self.subdiv_slider.set(min(10, self.subdiv_slider.get() + 1))


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()