import tkinter as tk
from tkinter import ttk, messagebox
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)
    
    def to_tuple(self):
        return (self.x, self.y)

class BezierQuadraticTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Квадратичная кривая Безье")
        
        self.canvas = tk.Canvas(self.frame, width=600, height=500, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=5, padx=5, pady=5)
        
        ttk.Label(self.frame, text="Параметр t (0-1):").grid(row=1, column=0, padx=5, pady=5)
        self.t_var = tk.DoubleVar(value=0.5)
        self.t_slider = tk.Scale(self.frame, from_=0, to=1, resolution=0.01, 
                                orient=tk.HORIZONTAL, variable=self.t_var,
                                command=self.update_curve)
        self.t_slider.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.frame, text="Количество разбиений:").grid(row=2, column=0, padx=5, pady=5)
        self.subdivisions_var = tk.IntVar(value=3)
        self.subdivisions_slider = tk.Scale(self.frame, from_=1, to=10, 
                                          orient=tk.HORIZONTAL, variable=self.subdivisions_var,
                                          command=self.update_curve)
        self.subdivisions_slider.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.frame, text="Количество сегментов:").grid(row=3, column=0, padx=5, pady=5)
        self.segments_var = tk.IntVar(value=1)
        self.segments_combo = ttk.Combobox(self.frame, textvariable=self.segments_var, 
                                          values=[1, 2, 3, 4, 5], state="readonly")
        self.segments_combo.grid(row=3, column=1, padx=5, pady=5)
        self.segments_combo.bind("<<ComboboxSelected>>", self.update_segments)
        
        ttk.Button(self.frame, text="Добавить точку", command=self.add_point_mode).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(self.frame, text="Очистить", command=self.clear).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(self.frame, text="Пример", command=self.load_example).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(self.frame, text="Построить кривую", command=self.draw_curve).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(self.frame, text="Пошагово", command=self.step_by_step).grid(row=2, column=3, padx=5, pady=5)
        ttk.Button(self.frame, text="Следующий шаг", command=self.next_step).grid(row=2, column=4, padx=5, pady=5)
        
        self.control_points = []
        self.curve_points = []
        self.intermediate_points = []
        self.segments = []
        self.adding_points = False
        self.show_intermediate = tk.BooleanVar(value=True)
        self.current_step = 0
        self.max_steps = 0
        
        ttk.Checkbutton(self.frame, text="Показывать промежуточные точки", 
                       variable=self.show_intermediate, command=self.update_curve).grid(row=3, column=2, columnspan=3)
        
        self.canvas.bind("<Button-1>", self.canvas_click)
        
    def add_point_mode(self):
        self.adding_points = True
        
    def canvas_click(self, event):
        if not self.adding_points:
            return
            
        point = Point(event.x, event.y)
        self.control_points.append(point)
        
        self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, 
                               fill="red", outline="red", tags="control_point")
        self.canvas.create_text(event.x, event.y-10, text=str(len(self.control_points)-1), 
                               fill="black", tags="control_label")
        
        self.update_segments()
        
    def update_segments(self, event=None):
        if len(self.control_points) >= 3:
            num_segments = max(1, len(self.control_points) - 2)
            self.segments_var.set(num_segments)
            self.segments_combo['values'] = list(range(1, num_segments + 1))
        
    def clear(self):
        self.canvas.delete("all")
        self.control_points = []
        self.curve_points = []
        self.intermediate_points = []
        self.segments = []
        self.current_step = 0
        self.max_steps = 0
        
    def load_example(self):
        self.clear()
        self.control_points = [
            Point(100, 400),
            Point(200, 100),
            Point(300, 400),
            Point(400, 100),
            Point(500, 400)
        ]
        
        for i, p in enumerate(self.control_points):
            self.canvas.create_oval(p.x-3, p.y-3, p.x+3, p.y+3, 
                                   fill="red", outline="red", tags="control_point")
            self.canvas.create_text(p.x, p.y-10, text=str(i), 
                                   fill="black", tags="control_label")
        
        self.update_segments()
        self.draw_curve()
    
    def bezier_quadratic(self, p0, p1, p2, t):
        return (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
    
    def recursive_subdivide(self, p0, p1, p2, t, depth, max_depth):
        if depth >= max_depth:
            return []
        
        p01 = (1-t) * p0 + t * p1
        p12 = (1-t) * p1 + t * p2
        p012 = (1-t) * p01 + t * p12
        
        if depth == self.current_step:
            self.intermediate_points.append((p0, p1, p2, p01, p12, p012))
        
        left = self.recursive_subdivide(p0, p01, p012, t, depth+1, max_depth)
        right = self.recursive_subdivide(p012, p12, p2, t, depth+1, max_depth)
        
        return left + [p012] + right
    
    def split_into_segments(self):
        self.segments = []
        num_segments = self.segments_var.get()
        
        if len(self.control_points) < 3:
            return []
        
        for i in range(num_segments):
            start_idx = i * (len(self.control_points) - 1) // num_segments
            if i == num_segments - 1:
                segment_points = self.control_points[-3:]
            else:
                segment_points = self.control_points[start_idx:start_idx+3]
            
            if len(segment_points) == 3:
                self.segments.append(segment_points)
    
    def draw_curve(self):
        if len(self.control_points) < 3:
            return
        
        self.canvas.delete("curve")
        self.canvas.delete("intermediate")
        self.curve_points = []
        self.intermediate_points = []
        
        t = self.t_var.get()
        subdivisions = self.subdivisions_var.get()
        
        self.split_into_segments()
        
        if not self.segments:
            return
        
        for i in range(len(self.control_points)-1):
            p1 = self.control_points[i]
            p2 = self.control_points[i+1]
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, 
                                   fill="gray", dash=(4,2), tags="curve")
        
        all_curve_points = []
        for segment_idx, segment in enumerate(self.segments):
            if len(segment) != 3:
                continue
                
            p0, p1, p2 = segment
            
            segment_curve_pts = []
            steps = 20
            for i in range(steps + 1):
                u = i / steps
                pt = self.bezier_quadratic(p0, p1, p2, u)
                segment_curve_pts.append(pt)
            
            all_curve_points.extend(segment_curve_pts)
            
            self.recursive_subdivide(p0, p1, p2, t, 0, subdivisions)
            
            mid_point = self.bezier_quadratic(p0, p1, p2, 0.5)
            self.canvas.create_text(mid_point.x, mid_point.y-15, 
                                   text=f"Сегмент {segment_idx+1}", 
                                   fill="blue", tags="curve")
        
        if self.show_intermediate.get():
            for points_tuple in self.intermediate_points:
                p0, p1, p2, p01, p12, p012 = points_tuple
                
                self.canvas.create_line(p01.x, p01.y, p12.x, p12.y, 
                                       fill="blue", width=1, tags="intermediate")
                self.canvas.create_line(p0.x, p0.y, p01.x, p01.y, 
                                       fill="lightblue", width=1, dash=(2,2), tags="intermediate")
                self.canvas.create_line(p1.x, p1.y, p12.x, p12.y, 
                                       fill="lightblue", width=1, dash=(2,2), tags="intermediate")
                
                self.canvas.create_oval(p01.x-2, p01.y-2, p01.x+2, p01.y+2, 
                                       fill="blue", outline="blue", tags="intermediate")
                self.canvas.create_oval(p12.x-2, p12.y-2, p12.x+2, p12.y+2, 
                                       fill="blue", outline="blue", tags="intermediate")
                self.canvas.create_oval(p012.x-2, p012.y-2, p012.x+2, p012.y+2, 
                                       fill="green", outline="green", tags="intermediate")
        
        for i in range(len(all_curve_points)-1):
            p1 = all_curve_points[i]
            p2 = all_curve_points[i+1]
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, 
                                   fill="red", width=2, tags="curve")
        
        info_text = f"Контрольных точек: {len(self.control_points)}, Сегментов: {len(self.segments)}"
        self.canvas.create_text(100, 20, text=info_text, 
                               fill="black", font=("Arial", 10), tags="curve")
    
    def step_by_step(self):
        if len(self.control_points) < 3:
            return
        
        self.current_step = 0
        self.max_steps = self.subdivisions_var.get()
        self.update_step_display()
    
    def next_step(self):
        if self.max_steps == 0:
            self.step_by_step()
            return
        
        if self.current_step < self.max_steps:
            self.current_step += 1
            self.update_step_display()
    
    def update_step_display(self):
        if len(self.control_points) < 3 or not self.segments:
            return
        
        self.canvas.delete("curve")
        self.canvas.delete("intermediate")
        self.intermediate_points = []
        
        t = self.t_var.get()
        
        for i in range(len(self.control_points)-1):
            p1 = self.control_points[i]
            p2 = self.control_points[i+1]
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, 
                                   fill="gray", dash=(4,2), tags="curve")
        
        for segment in self.segments:
            if len(segment) != 3:
                continue
                
            p0, p1, p2 = segment
            
            self.recursive_subdivide(p0, p1, p2, t, 0, self.current_step)
            
            if self.current_step == self.max_steps:
                curve_pts = []
                for i in range(21):
                    u = i / 20.0
                    pt = self.bezier_quadratic(p0, p1, p2, u)
                    curve_pts.append(pt)
                
                for i in range(len(curve_pts)-1):
                    p1_pt = curve_pts[i]
                    p2_pt = curve_pts[i+1]
                    self.canvas.create_line(p1_pt.x, p1_pt.y, p2_pt.x, p2_pt.y, 
                                           fill="red", width=2, tags="curve")
        
        for points_tuple in self.intermediate_points:
            p0, p1, p2, p01, p12, p012 = points_tuple
            
            self.canvas.create_line(p01.x, p01.y, p12.x, p12.y, 
                                   fill="blue", width=1, tags="intermediate")
            self.canvas.create_line(p0.x, p0.y, p01.x, p01.y, 
                                   fill="lightblue", width=1, dash=(2,2), tags="intermediate")
            self.canvas.create_line(p1.x, p1.y, p12.x, p12.y, 
                                   fill="lightblue", width=1, dash=(2,2), tags="intermediate")
            
            self.canvas.create_oval(p01.x-2, p01.y-2, p01.x+2, p01.y+2, 
                                   fill="blue", outline="blue", tags="intermediate")
            self.canvas.create_oval(p12.x-2, p12.y-2, p12.x+2, p12.y+2, 
                                   fill="blue", outline="blue", tags="intermediate")
            self.canvas.create_oval(p012.x-2, p012.y-2, p012.x+2, p012.y+2, 
                                   fill="green", outline="green", tags="intermediate")
        
        step_text = f"Шаг: {self.current_step}/{self.max_steps}"
        self.canvas.create_text(500, 20, text=step_text, 
                               fill="blue", font=("Arial", 10, "bold"), tags="curve")
    
    def update_curve(self, *args):
        if len(self.control_points) >= 3:
            self.draw_curve()

class ChaikinCurveTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Кривая Чайкина")
        
        self.canvas = tk.Canvas(self.frame, width=600, height=500, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Label(self.frame, text="Количество итераций:").grid(row=1, column=0, padx=5, pady=5)
        self.iterations_var = tk.IntVar(value=3)
        self.iterations_slider = tk.Scale(self.frame, from_=0, to=7, 
                                        orient=tk.HORIZONTAL, variable=self.iterations_var,
                                        command=self.update_curve)
        self.iterations_slider.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.frame, text="Добавить точку", command=self.add_point_mode).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.frame, text="Очистить", command=self.clear).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.frame, text="Пример", command=self.load_example).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(self.frame, text="Построить кривую", command=self.draw_curve).grid(row=2, column=3, padx=5, pady=5)
        
        self.control_points = []
        self.chaikin_points = []
        self.adding_points = False
        
        self.canvas.bind("<Button-1>", self.canvas_click)
        
    def add_point_mode(self):
        self.adding_points = True
        
    def canvas_click(self, event):
        if not self.adding_points:
            return
            
        point = Point(event.x, event.y)
        self.control_points.append(point)
        
        self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, 
                               fill="red", outline="red", tags="control_point")
        
        if len(self.control_points) > 1:
            last_point = self.control_points[-2]
            self.canvas.create_line(last_point.x, last_point.y, event.x, event.y, 
                                   fill="gray", dash=(4,2), tags="control_polygon")
        
        self.draw_curve()
        
    def clear(self):
        self.canvas.delete("all")
        self.control_points = []
        self.chaikin_points = []
        
    def load_example(self):
        self.clear()
        self.control_points = [
            Point(100, 300),
            Point(200, 100),
            Point(300, 400),
            Point(400, 200),
            Point(500, 300)
        ]
        
        for p in self.control_points:
            self.canvas.create_oval(p.x-3, p.y-3, p.x+3, p.y+3, 
                                   fill="red", outline="red", tags="control_point")
        
        for i in range(len(self.control_points)-1):
            p1 = self.control_points[i]
            p2 = self.control_points[i+1]
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, 
                                   fill="gray", dash=(4,2), tags="control_polygon")
        
        self.draw_curve()
    
    def chaikin_subdivision(self, points, iterations):
        if iterations == 0:
            return points
        
        new_points = []
        
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i+1]
            
            q = 0.75 * p0 + 0.25 * p1
            r = 0.25 * p0 + 0.75 * p1
            
            new_points.append(q)
            new_points.append(r)
        
        return self.chaikin_subdivision(new_points, iterations-1)
    
    def draw_curve(self):
        if len(self.control_points) < 2:
            return
        
        self.canvas.delete("chaikin")
        self.chaikin_points = []
        
        iterations = self.iterations_var.get()
        
        chaikin_pts = self.chaikin_subdivision(self.control_points, iterations)
        
        if len(chaikin_pts) > 1:
            for i in range(len(chaikin_pts)-1):
                p1 = chaikin_pts[i]
                p2 = chaikin_pts[i+1]
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, 
                                       fill="blue", width=2, tags="chaikin")
            
            for pt in chaikin_pts:
                self.canvas.create_oval(pt.x-2, pt.y-2, pt.x+2, pt.y+2, 
                                       fill="blue", outline="blue", tags="chaikin")
        
        self.canvas.create_text(50, 20, text=f"Итерация: {iterations}", 
                               fill="black", tags="chaikin")
    
    def update_curve(self, *args):
        if len(self.control_points) >= 2:
            self.draw_curve()

class DooSabinSurfaceTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Поверхность Ду-Сабина")
        
        self.canvas = tk.Canvas(self.frame, width=600, height=500, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Label(self.frame, text="Количество итераций:").grid(row=1, column=0, padx=5, pady=5)
        self.iterations_var = tk.IntVar(value=2)
        self.iterations_slider = tk.Scale(self.frame, from_=0, to=5, 
                                        orient=tk.HORIZONTAL, variable=self.iterations_var,
                                        command=self.update_surface)
        self.iterations_slider.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.frame, text="Тип поверхности:").grid(row=2, column=0, padx=5, pady=5)
        self.surface_type = tk.StringVar(value="quad")
        
        ttk.Radiobutton(self.frame, text="Четырехугольник", variable=self.surface_type, 
                       value="quad", command=self.load_example).grid(row=2, column=1, padx=5, pady=5)
        ttk.Radiobutton(self.frame, text="Треугольник", variable=self.surface_type, 
                       value="triangle", command=self.load_example).grid(row=2, column=2, padx=5, pady=5)
        ttk.Radiobutton(self.frame, text="Пятиугольник", variable=self.surface_type, 
                       value="pentagon", command=self.load_example).grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Button(self.frame, text="Очистить", command=self.clear).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.frame, text="Пример", command=self.load_example).grid(row=3, column=1, padx=5, pady=5)
        
        self.vertices = []
        self.faces = []
        self.edges = []
        self.face_points_history = []
        
    def clear(self):
        self.canvas.delete("all")
        self.vertices = []
        self.faces = []
        self.edges = []
        self.face_points_history = []
        
    def load_example(self):
        self.clear()
        
        surface_type = self.surface_type.get()
        
        if surface_type == "quad":
            self.vertices = [
                Point(200, 200),
                Point(400, 200),
                Point(400, 400),
                Point(200, 400)
            ]
        elif surface_type == "triangle":
            self.vertices = [
                Point(300, 150),
                Point(450, 350),
                Point(150, 350)
            ]
        elif surface_type == "pentagon":
            center = Point(300, 250)
            radius = 150
            for i in range(5):
                angle = 2 * math.pi * i / 5
                x = center.x + radius * math.cos(angle)
                y = center.y + radius * math.sin(angle)
                self.vertices.append(Point(x, y))
        
        for i, v in enumerate(self.vertices):
            self.canvas.create_oval(v.x-4, v.y-4, v.x+4, v.y+4, 
                                   fill="red", outline="red", tags="vertex")
            self.canvas.create_text(v.x, v.y-10, text=str(i), 
                                   fill="black", tags="vertex_label")
        
        self.faces = [list(range(len(self.vertices)))]
        self.edges = []
        for i in range(len(self.vertices)):
            self.edges.append((i, (i+1) % len(self.vertices)))
        
        self.draw_mesh()
        self.update_surface()
    
    def draw_mesh(self):
        self.canvas.delete("mesh")
        
        for edge in self.edges:
            v1 = self.vertices[edge[0]]
            v2 = self.vertices[edge[1]]
            self.canvas.create_line(v1.x, v1.y, v2.x, v2.y, 
                                   fill="black", width=2, tags="mesh")
        
        if self.faces and self.vertices:
            for face in self.faces:
                points = [self.vertices[i].to_tuple() for i in face]
                if len(points) >= 3:
                    self.canvas.create_polygon(points, fill="lightblue", 
                                              outline="black", width=1, tags="mesh")
    
    def doosabin_subdivision(self, vertices, faces, edges):
        new_vertices = []
        new_faces = []
        new_edges = []
        face_points = []
        
        for face in faces:
            avg = Point(0, 0)
            for vertex_idx in face:
                avg = avg + vertices[vertex_idx]
            avg = avg / len(face)
            face_points.append(avg)
        
        edge_points = []
        edge_to_faces = {}
        
        for edge_idx, edge in enumerate(edges):
            v1_idx, v2_idx = edge
            v1 = vertices[v1_idx]
            v2 = vertices[v2_idx]
            
            adjacent_faces = []
            for face_idx, face in enumerate(faces):
                has_v1 = any(v == v1_idx for v in face)
                has_v2 = any(v == v2_idx for v in face)
                
                if has_v1 and has_v2:
                    idx1 = face.index(v1_idx)
                    idx2 = face.index(v2_idx)
                    
                    if (abs(idx1 - idx2) == 1 or 
                        (idx1 == 0 and idx2 == len(face)-1) or 
                        (idx2 == 0 and idx1 == len(face)-1)):
                        adjacent_faces.append(face_idx)
            
            if len(adjacent_faces) == 2:
                edge_point = (v1 + v2 + face_points[adjacent_faces[0]] + 
                            face_points[adjacent_faces[1]]) / 4
                edge_points.append(edge_point)
                edge_to_faces[edge_idx] = adjacent_faces
        
        vertex_points = []
        for vertex_idx, vertex in enumerate(vertices):
            incident_edges = []
            for edge_idx, edge in enumerate(edges):
                if vertex_idx in edge:
                    incident_edges.append(edge_idx)
            
            if incident_edges:
                Q = Point(0, 0)
                adjacent_faces_set = set()
                
                for edge_idx in incident_edges:
                    if edge_idx in edge_to_faces:
                        for face_idx in edge_to_faces[edge_idx]:
                            adjacent_faces_set.add(face_idx)
                
                for face_idx in adjacent_faces_set:
                    Q = Q + face_points[face_idx]
                
                if adjacent_faces_set:
                    Q = Q / len(adjacent_faces_set)
                
                R = Point(0, 0)
                for edge_idx in incident_edges:
                    edge = edges[edge_idx]
                    v1 = vertices[edge[0]]
                    v2 = vertices[edge[1]]
                    mid = (v1 + v2) / 2
                    R = R + mid
                
                R = R / len(incident_edges)
                
                S = vertex
                n = len(incident_edges)
                new_vertex = (Q + 2*R + (n-3)*S) / n
                vertex_points.append(new_vertex)
        
        new_vertices = face_points + edge_points + vertex_points
        
        for i in range(len(faces)):
            new_faces.append([i])
        
        for edge_idx, edge in enumerate(edges):
            if edge_idx in edge_to_faces:
                new_face = [
                    edge_idx + len(face_points),
                    edge_to_faces[edge_idx][0],
                    edge[0] + len(face_points) + len(edge_points),
                    edge_to_faces[edge_idx][1]
                ]
                new_faces.append(new_face)
        
        for vertex_idx in range(len(vertices)):
            incident_edges_for_vertex = []
            adjacent_faces_for_vertex = set()
            
            for edge_idx, edge in enumerate(edges):
                if vertex_idx in edge:
                    incident_edges_for_vertex.append(edge_idx)
                    if edge_idx in edge_to_faces:
                        for face_idx in edge_to_faces[edge_idx]:
                            adjacent_faces_for_vertex.add(face_idx)
            
            new_face = [vertex_idx + len(face_points) + len(edge_points)]
            
            for edge_idx in incident_edges_for_vertex:
                new_face.append(edge_idx + len(face_points))
            
            for face_idx in adjacent_faces_for_vertex:
                new_face.append(face_idx)
            
            new_faces.append(new_face)
        
        for face in new_faces:
            for i in range(len(face)):
                v1 = face[i]
                v2 = face[(i+1) % len(face)]
                edge = (min(v1, v2), max(v1, v2))
                if edge not in new_edges:
                    new_edges.append(edge)
        
        return new_vertices, new_faces, new_edges, face_points
    
    def draw_surface(self, vertices, faces, edges, iteration):
        self.canvas.delete(f"surface_{iteration}")
        
        for i, v in enumerate(vertices):
            if i >= len(vertices):
                continue
            color = "green" if iteration > 0 else "red"
            size = 3 if iteration > 0 else 4
            self.canvas.create_oval(v.x-size, v.y-size, v.x+size, v.y+size, 
                                   fill=color, outline=color, tags=f"surface_{iteration}")
        
        for edge in edges:
            if edge[0] < len(vertices) and edge[1] < len(vertices):
                v1 = vertices[edge[0]]
                v2 = vertices[edge[1]]
                color = "blue" if iteration > 0 else "black"
                width = 1 if iteration > 0 else 2
                self.canvas.create_line(v1.x, v1.y, v2.x, v2.y, 
                                       fill=color, width=width, tags=f"surface_{iteration}")
        
        for face in faces:
            if len(face) >= 3 and all(v < len(vertices) for v in face):
                points = [vertices[i].to_tuple() for i in face]
                fill_color = "#E0F7FA" if iteration > 0 else "lightblue"
                self.canvas.create_polygon(points, fill=fill_color, 
                                          outline="blue", width=1, tags=f"surface_{iteration}")
    
    def update_surface(self, *args):
        if not self.faces:
            return
        
        for i in range(1, 6):
            self.canvas.delete(f"surface_{i}")
        
        iterations = self.iterations_var.get()
        
        current_vertices = self.vertices.copy()
        current_faces = self.faces.copy()
        current_edges = self.edges.copy()
        self.face_points_history = []
        
        for i in range(iterations):
            current_vertices, current_faces, current_edges, face_points = self.doosabin_subdivision(
                current_vertices, current_faces, current_edges
            )
            self.face_points_history.append(face_points)
            self.draw_surface(current_vertices, current_faces, current_edges, i+1)
        
        info_text = f"Итерация: {iterations}, Вершин: {len(current_vertices)}, Граней: {len(current_faces)}"
        self.canvas.create_text(300, 20, text=info_text, 
                               fill="black", font=("Arial", 10), tags="info")

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы построения кривых и поверхностей")
        self.root.geometry("850x750")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.bezier_tab = BezierQuadraticTab(self.notebook)
        self.chaikin_tab = ChaikinCurveTab(self.notebook)
        self.doosabin_tab = DooSabinSurfaceTab(self.notebook)
        
        info_frame = ttk.Frame(root)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        info_text = """
        Вариант 4. Реализованы алгоритмы:
        1. Квадратичная кривая Безье (произвольное количество вершин, пошаговое выполнение, выбор параметра разбиения)
        3. Кривая Чайкина
        5. Поверхность Ду-Сабина
        6. Отображение контрольных точек и уточненных полигонов
        """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()