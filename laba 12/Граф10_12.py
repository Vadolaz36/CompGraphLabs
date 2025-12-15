import tkinter as tk
from tkinter import ttk
import math
import json

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def project(self, canvas_width, canvas_height, scale, offset_x, offset_y):
        x_proj = self.x * scale + offset_x
        y_proj = -self.y * scale + offset_y
        return x_proj, y_proj

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Построение кривых и поверхностей")
        self.root.geometry("1200x700")
        
        self.canvas_width = 800
        self.canvas_height = 600
        self.scale = 50
        self.offset_x = self.canvas_width // 2
        self.offset_y = self.canvas_height // 2
        
        self.current_method = "bezier_quad"
        self.control_points = []
        self.subdivisions = 3
        self.t_parameter = 0.5
        self.step_mode = False
        self.current_step = 0
        
        self.examples = {
            "bezier_quad": [
                Point3D(-4, 2, 0),
                Point3D(0, 4, 0),
                Point3D(4, 2, 0),
                Point3D(6, -1, 0),
                Point3D(4, -3, 0),
                Point3D(0, -2, 0),
                Point3D(-4, -3, 0),
                Point3D(-6, -1, 0)
            ],
            "bezier_cubic": [
                Point3D(-5, 0, 0),
                Point3D(-3, 4, 0),
                Point3D(0, 4, 0),
                Point3D(3, 0, 0),
                Point3D(3, -3, 0),
                Point3D(0, -5, 0),
                Point3D(-3, -3, 0),
                Point3D(-5, 0, 0)
            ],
            "chaikin": [
                Point3D(-5, -3, 0),
                Point3D(-2, 4, 0),
                Point3D(0, 1, 0),
                Point3D(3, 5, 0),
                Point3D(5, -2, 0),
                Point3D(2, -4, 0),
                Point3D(-1, -1, 0)
            ],
            "bezier_surface": [
                # 4x4 сетка для поверхности Безье
                Point3D(-3, -3, 2), Point3D(-1, -3, 0), Point3D(1, -3, -1), Point3D(3, -3, 1),
                Point3D(-3, -1, 1), Point3D(-1, -1, 3), Point3D(1, -1, 2), Point3D(3, -1, 0),
                Point3D(-3, 1, 0), Point3D(-1, 1, 2), Point3D(1, 1, 3), Point3D(3, 1, 1),
                Point3D(-3, 3, 1), Point3D(-1, 3, -1), Point3D(1, 3, 0), Point3D(3, 3, 2)
            ],
            "doo_sabin": [
                Point3D(-3, 0, 0),
                Point3D(-1, 3, 1),
                Point3D(1, 3, -1),
                Point3D(3, 0, 0),
                Point3D(1, -3, 1),
                Point3D(-1, -3, -1),
                Point3D(-2, -1, 2),
                Point3D(2, -1, -2)
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
        style.map('Example.TButton',
                 background=[('active', '#45a049')])

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
        
        ttk.Label(parent, text="Параметры:", style='Title.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
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
        
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Button(parent, text="Загрузить пример", command=self.load_example, 
                  style='Example.TButton').pack(fill=tk.X, pady=5)
        
        self.step_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Пошаговый режим", variable=self.step_var, 
                       command=self.toggle_step_mode).pack(anchor=tk.W, pady=5)
        
        self.info_label = ttk.Label(parent, text="Точек: 0", font=('Arial', 10))
        self.info_label.pack(anchor=tk.W, pady=10)

    def setup_points_table(self, parent):
        frame = ttk.LabelFrame(parent, text="Точки управления", padding=5)
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
        canvas_frame = ttk.LabelFrame(parent, text="Визуализация", padding=10)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, 
                               height=self.canvas_height, bg="white", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        
        self.draw_grid()

    def load_example(self):
        """Загружает пример для текущего метода"""
        if self.current_method in self.examples:
            self.control_points = [Point3D(p.x, p.y, p.z) for p in self.examples[self.current_method]]
            self.update_points_list()
            self.draw()
            
            # Установим оптимальные параметры для примера
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
            self.canvas.create_line(x, 0, x, self.canvas_height, fill="#e0e0e0", tags="grid")
            y = i * self.scale + self.offset_y
            self.canvas.create_line(0, y, self.canvas_width, y, fill="#e0e0e0", tags="grid")
        
        self.canvas.create_line(self.offset_x, 0, self.offset_x, self.canvas_height, 
                               fill="#888", width=1, tags="grid")
        self.canvas.create_line(0, self.offset_y, self.canvas_width, self.offset_y, 
                               fill="#888", width=1, tags="grid")
        
        for i in range(-10, 11):
            x = i * self.scale + self.offset_x
            self.canvas.create_text(x, self.offset_y + 15, text=str(i), fill="#666", font=("Arial", 8), tags="grid")
            if i != 0:
                y = i * self.scale + self.offset_y
                self.canvas.create_text(self.offset_x + 15, y, text=str(-i), fill="#666", font=("Arial", 8), tags="grid")

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
        z = random.uniform(-2, 2) if "surface" in self.current_method else 0
        self.control_points.append(Point3D(x, y, z))
        self.update_points_list()
        self.draw()

    def canvas_click(self, event):
        x = (event.x - self.offset_x) / self.scale
        y = -(event.y - self.offset_y) / self.scale
        z = 0 if "surface" not in self.current_method else (len(self.control_points) / 10.0 - 2)
        
        if event.state & 0x0004:  # Ctrl key
            if self.control_points:
                min_dist = float('inf')
                closest_idx = -1
                for i, p in enumerate(self.control_points):
                    dist = math.sqrt((p.x - x)**2 + (p.y - y)**2)
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = i
                if min_dist < 0.5:
                    del self.control_points[closest_idx]
                    self.update_points_list()
        else:
            self.control_points.append(Point3D(x, y, z))
            self.update_points_list()
        
        self.draw()

    def canvas_drag(self, event):
        if not self.control_points:
            return
        
        x = (event.x - self.offset_x) / self.scale
        y = -(event.y - self.offset_y) / self.scale
        
        min_dist = float('inf')
        closest_idx = -1
        for i, p in enumerate(self.control_points):
            px, py = self.project_point(p)
            dist = math.sqrt((px - event.x)**2 + (py - event.y)**2)
            if dist < min_dist and dist < 20:
                min_dist = dist
                closest_idx = i
        
        if closest_idx >= 0:
            self.control_points[closest_idx].x = x
            self.control_points[closest_idx].y = y
            self.update_points_list()
            self.draw()

    def update_points_list(self):
        for widget in self.points_frame.winfo_children():
            widget.destroy()
        
        for i, point in enumerate(self.control_points):
            frame = ttk.Frame(self.points_frame)
            frame.pack(fill=tk.X, pady=1)
            
            ttk.Label(frame, text=f"{i}:", width=4).pack(side=tk.LEFT)
            ttk.Label(frame, text=f"({point.x:.2f}, {point.y:.2f}", width=15).pack(side=tk.LEFT)
            ttk.Label(frame, text=f"z={point.z:.2f})", width=10).pack(side=tk.LEFT)
            
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

    def project_point(self, point):
        return point.project(self.canvas_width, self.canvas_height, self.scale, self.offset_x, self.offset_y)

    def bernstein(self, i, n, t):
        from math import comb
        return comb(n, i) * (t**i) * ((1-t)**(n-i))

    def bezier_quad(self, points, t):
        result = []
        if len(points) < 3:
            return result
        
        for seg in range(0, len(points)-2, 2):
            if seg+2 >= len(points):
                break
            p0, p1, p2 = points[seg], points[seg+1], points[seg+2]
            x = (1-t)**2 * p0.x + 2*(1-t)*t * p1.x + t**2 * p2.x
            y = (1-t)**2 * p0.y + 2*(1-t)*t * p1.y + t**2 * p2.y
            z = (1-t)**2 * p0.z + 2*(1-t)*t * p1.z + t**2 * p2.z
            result.append(Point3D(x, y, z))
        
        return result

    def bezier_cubic(self, points, t):
        result = []
        if len(points) < 4:
            return result
        
        for seg in range(0, len(points)-3, 3):
            if seg+3 >= len(points):
                break
            p0, p1, p2, p3 = points[seg], points[seg+1], points[seg+2], points[seg+3]
            x = (1-t)**3 * p0.x + 3*(1-t)**2*t * p1.x + 3*(1-t)*t**2 * p2.x + t**3 * p3.x
            y = (1-t)**3 * p0.y + 3*(1-t)**2*t * p1.y + 3*(1-t)*t**2 * p2.y + t**3 * p3.y
            z = (1-t)**3 * p0.z + 3*(1-t)**2*t * p1.z + 3*(1-t)*t**2 * p2.z + t**3 * p3.z
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
            for i in range(len(current)-1):
                p0 = current[i]
                p1 = current[i+1]
                q = Point3D(0.75*p0.x + 0.25*p1.x, 0.75*p0.y + 0.25*p1.y, 0.75*p0.z + 0.25*p1.z)
                r = Point3D(0.25*p0.x + 0.75*p1.x, 0.25*p0.y + 0.75*p1.y, 0.25*p0.z + 0.75*p1.z)
                new_points.extend([q, r])
            current = new_points
        
        return current

    def bezier_surface(self, points, subdivisions):
        if len(points) < 4:
            return []
        
        n = int(math.sqrt(len(points)))
        if n < 2:
            n = 2
        if n*n > len(points):
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
                        idx = ii*n + jj
                        if idx < len(points):
                            basis = self.bernstein(ii, n-1, u) * self.bernstein(jj, n-1, v)
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
                p1 = current[(i+1)%n]
                p2 = current[(i+2)%n]
                
                face_center = Point3D((p0.x+p1.x+p2.x)/3, (p0.y+p1.y+p2.y)/3, (p0.z+p1.z+p2.z)/3)
                edge1_mid = Point3D((p0.x+p1.x)/2, (p0.y+p1.y)/2, (p0.z+p1.z)/2)
                edge2_mid = Point3D((p1.x+p2.x)/2, (p1.y+p2.y)/2, (p1.z+p2.z)/2)
                
                new_point = Point3D(
                    (p0.x + edge1_mid.x + edge2_mid.x + face_center.x)/4,
                    (p0.y + edge1_mid.y + edge2_mid.y + face_center.y)/4,
                    (p0.z + edge1_mid.z + edge2_mid.z + face_center.z)/4
                )
                new_points.append(new_point)
            
            current = new_points
        
        return current

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        
        for i, point in enumerate(self.control_points):
            x, y = self.project_point(point)
            color = "#ff4444" if i % 3 == 0 else "#44aaff" if i % 3 == 1 else "#44ff44"
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill=color, outline="black", width=1, tags="points")
            self.canvas.create_text(x+8, y-8, text=str(i), fill="black", font=("Arial", 8), tags="points")
        
        if len(self.control_points) > 1:
            points_proj = [self.project_point(p) for p in self.control_points]
            for i in range(len(points_proj)-1):
                x1, y1 = points_proj[i]
                x2, y2 = points_proj[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill="#aaa", dash=(2,2), width=1, tags="polygon")
        
        if self.current_method == "bezier_quad" and len(self.control_points) >= 3:
            curve_points = []
            steps = 50 if not self.step_mode else min(50, (self.current_step + 1) * 10)
            for t in [i/steps for i in range(steps+1)]:
                curve_points.extend(self.bezier_quad(self.control_points, t))
            self.draw_curve(curve_points, "#0066cc")
        
        elif self.current_method == "bezier_cubic" and len(self.control_points) >= 4:
            curve_points = []
            steps = 50 if not self.step_mode else min(50, (self.current_step + 1) * 10)
            for t in [i/steps for i in range(steps+1)]:
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

    def draw_curve(self, points, color, close=False):
        if len(points) < 2:
            return
        
        for i in range(len(points)-1):
            x1, y1 = self.project_point(points[i])
            x2, y2 = self.project_point(points[i+1])
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2, tags="curve")
        
        if close and len(points) > 2:
            x1, y1 = self.project_point(points[-1])
            x2, y2 = self.project_point(points[0])
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2, tags="curve")

    def draw_surface(self, grid, color):
        if not grid or len(grid) < 2:
            return
        
        n = len(grid)
        
        for i in range(n):
            for j in range(n-1):
                x1, y1 = self.project_point(grid[i][j])
                x2, y2 = self.project_point(grid[i][j+1])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, tags="surface")
        
        for j in range(n):
            for i in range(n-1):
                x1, y1 = self.project_point(grid[i][j])
                x2, y2 = self.project_point(grid[i+1][j])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, tags="surface")
        
        for i in range(n):
            for j in range(n):
                if (i+j) % 2 == 0:
                    x, y = self.project_point(grid[i][j])
                    self.canvas.create_oval(x-2, y-2, x+2, y+2, fill=color, outline="", tags="surface")

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