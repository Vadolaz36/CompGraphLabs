import tkinter as tk
import math

class Vector3D:
    """3D вектор для работы с координатами"""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length > 0:
            return Vector3D(self.x/length, self.y/length, self.z/length)
        return self
    
    def to_list(self):
        return [self.x, self.y, self.z]

class Matrix3D:
    """Матрица 3x3 для преобразований"""
    @staticmethod
    def rotation_x(angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return [
            [1, 0, 0],
            [0, cos_a, -sin_a],
            [0, sin_a, cos_a]
        ]
    
    @staticmethod
    def rotation_y(angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return [
            [cos_a, 0, sin_a],
            [0, 1, 0],
            [-sin_a, 0, cos_a]
        ]
    
    @staticmethod
    def rotation_z(angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return [
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ]
    
    @staticmethod
    def multiply_vector(matrix, vector):
        x = vector.x * matrix[0][0] + vector.y * matrix[0][1] + vector.z * matrix[0][2]
        y = vector.x * matrix[1][0] + vector.y * matrix[1][1] + vector.z * matrix[1][2]
        z = vector.x * matrix[2][0] + vector.y * matrix[2][1] + vector.z * matrix[2][2]
        return Vector3D(x, y, z)

class Face:
    """Грань многоугольника в 3D"""
    def __init__(self, vertices, color, obj_id, face_id):
        self.vertices = vertices  # список Vector3D
        self.color = color
        self.obj_id = obj_id
        self.face_id = face_id
        self.normal = self.calculate_normal()
        self.centroid = self.calculate_centroid()
        self.z_min = min(v.z for v in vertices)
        self.z_max = max(v.z for v in vertices)
    
    def calculate_normal(self):
        """Вычисляет нормаль грани"""
        if len(self.vertices) < 3:
            return Vector3D(0, 0, 1)
        v1 = self.vertices[1] - self.vertices[0]
        v2 = self.vertices[2] - self.vertices[0]
        normal = v1.cross(v2)
        return normal.normalize()
    
    def calculate_centroid(self):
        """Вычисляет центр масс грани"""
        sum_x = sum(v.x for v in self.vertices)
        sum_y = sum(v.y for v in self.vertices)
        sum_z = sum(v.z for v in self.vertices)
        n = len(self.vertices)
        return Vector3D(sum_x/n, sum_y/n, sum_z/n)
    
    def project_to_2d(self, camera_pos, fov=500):
        """Проецирует грань на 2D плоскость"""
        projected_points = []
        for vertex in self.vertices:
            # Смещение относительно камеры
            dx = vertex.x - camera_pos.x
            dy = vertex.y - camera_pos.y
            dz = vertex.z - camera_pos.z
            
            # Если точка позади камеры, возвращаем None
            if dz <= 1:
                return None
            
            # Ортографическая проекция (проще для отладки)
            # Можно переключить на перспективную, раскомментировав строку ниже
            scale = 1.0  # Ортографическая
            # scale = fov / (dz + fov/2)  # Перспективная
            
            x_proj = 300 + dx * scale * 2
            y_proj = 300 - dy * scale * 2
            
            projected_points.append((x_proj, y_proj))
        
        return projected_points
    
    def get_depth(self, x, y):
        """Возвращает глубину грани в точке (x, y)"""
        # Уравнение плоскости: Ax + By + Cz + D = 0
        A, B, C = self.normal.x, self.normal.y, self.normal.z
        # Используем первую точку для нахождения D
        D = -(A * self.vertices[0].x + B * self.vertices[0].y + C * self.vertices[0].z)
        
        if C != 0:
            z = -(A * x + B * y + D) / C
            return z
        return float('inf')
    
    def get_bounding_box_2d(self, camera_pos):
        """Возвращает ограничивающий прямоугольник в 2D"""
        projected = self.project_to_2d(camera_pos)
        if not projected:
            return None
        
        xs = [p[0] for p in projected]
        ys = [p[1] for p in projected]
        
        # Добавляем небольшой запас
        padding = 2
        return (min(xs)-padding, min(ys)-padding, max(xs)+padding, max(ys)+padding)

class Warnock3D:
    """Реализация 3D алгоритма Варнока"""
    def __init__(self):
        self.subdivisions = []
        self.current_step = 0
        self.max_depth = 4  # Уменьшаем глубину для скорости
    
    def classify_face_vs_window(self, face, window, camera_pos):
        """Классифицирует грань относительно окна"""
        bbox = face.get_bounding_box_2d(camera_pos)
        if not bbox:
            return "outside"
        
        x1, y1, x2, y2 = window
        bx1, by1, bx2, by2 = bbox
        
        # Проверяем, пересекаются ли прямоугольники
        if bx2 < x1 or bx1 > x2 or by2 < y1 or by1 > y2:
            return "outside"
        
        # Проверяем, находится ли окно полностью внутри ограничивающего прямоугольника
        if x1 >= bx1 and x2 <= bx2 and y1 >= by1 and y2 <= by2:
            return "surrounding"
        
        # Проверяем, находится ли грань полностью внутри окна
        if bx1 >= x1 and bx2 <= x2 and by1 >= y1 and by2 <= y2:
            return "inside"
        
        # Иначе - пересекает
        return "intersecting"
    
    def analyze_window(self, window, faces, camera_pos, depth):
        """Анализирует окно и возвращает решение"""
        x1, y1, x2, y2 = window
        
        # Классификация всех граней
        inside_faces = []
        intersecting_faces = []
        surrounding_faces = []
        
        for face in faces:
            classification = self.classify_face_vs_window(face, window, camera_pos)
            
            if classification == "inside":
                inside_faces.append(face)
            elif classification == "intersecting":
                intersecting_faces.append(face)
            elif classification == "surrounding":
                surrounding_faces.append(face)
        
        # Определение простых случаев
        step_info = {
            'window': window,
            'depth': depth,
            'inside': inside_faces,
            'intersecting': intersecting_faces,
            'surrounding': surrounding_faces,
            'decision': None,
            'color': None,
            'obj_id': None
        }
        
        # Случай 1: Нет граней
        if not inside_faces and not intersecting_faces and not surrounding_faces:
            step_info['decision'] = "Нет граней - фон"
            step_info['color'] = "white"
            return step_info
        
        # Случай 2: Одна внутренняя/пересекающая грань
        if len(inside_faces) + len(intersecting_faces) == 1 and not surrounding_faces:
            face = inside_faces[0] if inside_faces else intersecting_faces[0]
            step_info['decision'] = f"Одна грань - объект {face.obj_id}"
            step_info['color'] = face.color
            step_info['obj_id'] = face.obj_id
            return step_info
        
        # Случай 3: Одна охватывающая грань
        if len(surrounding_faces) == 1 and not inside_faces and not intersecting_faces:
            face = surrounding_faces[0]
            step_info['decision'] = f"Охватывающая грань - объект {face.obj_id}"
            step_info['color'] = face.color
            step_info['obj_id'] = face.obj_id
            return step_info
        
        # Сложный случай - нужно разбивать
        step_info['decision'] = "Сложный случай - разбиваем"
        return step_info
    
    def subdivide(self, window, faces, camera_pos, depth=0):
        """Рекурсивное разбиение окна"""
        # Проверяем условие остановки
        if depth >= self.max_depth or (window[2] - window[0] <= 4) or (window[3] - window[1] <= 4):
            # Достигли минимального размера - определяем цвет по ближайшей грани
            result = self.analyze_window(window, faces, camera_pos, depth)
            if result['color'] is None:
                # Если нет однозначного цвета, ищем ближайшую грань
                closest_face = None
                min_z = float('inf')
                center_x = (window[0] + window[2]) / 2
                center_y = (window[1] + window[3]) / 2
                
                for face in faces:
                    bbox = face.get_bounding_box_2d(camera_pos)
                    if bbox:
                        bx1, by1, bx2, by2 = bbox
                        if bx1 <= center_x <= bx2 and by1 <= center_y <= by2:
                            z = face.get_depth(center_x, center_y)
                            if z < min_z:
                                min_z = z
                                closest_face = face
                
                if closest_face:
                    result['color'] = closest_face.color
                    result['obj_id'] = closest_face.obj_id
                    result['decision'] = f"Минимальное окно - объект {closest_face.obj_id}"
                else:
                    result['color'] = "white"
                    result['decision'] = "Минимальное окно - фон"
            
            result['action'] = "Минимальное окно"
            self.subdivisions.append(result)
            return result
        
        # Анализируем текущее окно
        analysis = self.analyze_window(window, faces, camera_pos, depth)
        
        if analysis['decision'].startswith("Сложный случай"):
            # Разбиваем окно
            analysis['action'] = "Разбиение"
            self.subdivisions.append(analysis)
            
            x1, y1, x2, y2 = window
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Создаем 4 подокна
            subwindows = [
                (x1, y1, mid_x, mid_y),
                (mid_x, y1, x2, mid_y),
                (x1, mid_y, mid_x, y2),
                (mid_x, mid_y, x2, y2)
            ]
            
            # Для каждого подокна находим грани, которые его пересекают
            all_results = []
            for subwindow in subwindows:
                relevant_faces = []
                for face in faces:
                    classification = self.classify_face_vs_window(face, subwindow, camera_pos)
                    if classification != "outside":
                        relevant_faces.append(face)
                
                if relevant_faces:
                    result = self.subdivide(subwindow, relevant_faces, camera_pos, depth + 1)
                    all_results.append(result)
                else:
                    # Нет граней - фон
                    empty_result = {
                        'window': subwindow,
                        'depth': depth + 1,
                        'color': 'white',
                        'decision': 'Нет граней - фон',
                        'action': 'Пустое окно'
                    }
                    self.subdivisions.append(empty_result)
                    all_results.append(empty_result)
            
            # Определяем цвет для всего окна на основе результатов подокон
            colors = [r['color'] for r in all_results if r['color'] != 'white']
            if colors:
                # Берем первый небелый цвет (можно улучшить логику)
                analysis['color'] = colors[0]
                for r in all_results:
                    if r['color'] == colors[0] and 'obj_id' in r:
                        analysis['obj_id'] = r['obj_id']
                        break
                analysis['decision'] = f"После разбиения - объект {analysis.get('obj_id', '?')}"
            else:
                analysis['color'] = 'white'
                analysis['decision'] = "После разбиения - фон"
            
            return analysis
        else:
            # Простой случай - сразу знаем цвет
            analysis['action'] = "Простой случай"
            self.subdivisions.append(analysis)
            return analysis

class Scene3D:
    """3D сцена с объектами"""
    def __init__(self):
        self.faces = []
        self.camera_pos = Vector3D(0, 0, -500)  # Камера сзади
        self.rotation_x = 0
        self.rotation_y = 0
        self.scale = 1.0
        self.original_faces = []  # Сохраняем оригинальные грани
        
        # Стандартные цвета Tkinter
        self.colors = [
            'red', 'green', 'blue', 'yellow', 
            'cyan', 'magenta', 'orange', 'purple',
            'pink', 'brown', 'gray', 'lime',
            'navy', 'teal', 'olive', 'maroon'
        ]
    
    def create_cube(self, center, size, obj_id):
        """Создает куб"""
        x, y, z = center.x, center.y, center.z
        s = size / 2
        
        # Вершины куба
        vertices = [
            Vector3D(x-s, y-s, z-s), Vector3D(x+s, y-s, z-s),
            Vector3D(x+s, y+s, z-s), Vector3D(x-s, y+s, z-s),
            Vector3D(x-s, y-s, z+s), Vector3D(x+s, y-s, z+s),
            Vector3D(x+s, y+s, z+s), Vector3D(x-s, y+s, z+s)
        ]
        
        # Грани куба (каждая грань - 4 вершины)
        faces_vertices = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # Передняя
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # Задняя
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Нижняя
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Верхняя
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # Левая
            [vertices[1], vertices[2], vertices[6], vertices[5]]   # Правая
        ]
        
        # Цвет для всего куба
        color = self.colors[obj_id % len(self.colors)]
        
        for i, verts in enumerate(faces_vertices):
            face = Face(verts, color, obj_id, i)
            self.faces.append(face)
            self.original_faces.append((verts, color, obj_id, i))
    
    def create_pyramid(self, center, size, obj_id):
        """Создает пирамиду"""
        x, y, z = center.x, center.y, center.z
        s = size / 2
        
        vertices = [
            Vector3D(x, y+s, z),      # Верх
            Vector3D(x-s, y-s, z-s),  # Основание 1
            Vector3D(x+s, y-s, z-s),  # Основание 2
            Vector3D(x+s, y-s, z+s),  # Основание 3
            Vector3D(x-s, y-s, z+s)   # Основание 4
        ]
        
        # Грани пирамиды
        faces_vertices = [
            [vertices[0], vertices[1], vertices[2]],  # Передняя
            [vertices[0], vertices[2], vertices[3]],  # Правая
            [vertices[0], vertices[3], vertices[4]],  # Задняя
            [vertices[0], vertices[4], vertices[1]],  # Левая
            [vertices[1], vertices[2], vertices[3], vertices[4]]  # Основание
        ]
        
        # Цвет для всей пирамиды
        color = self.colors[obj_id % len(self.colors)]
        
        for i, verts in enumerate(faces_vertices):
            face = Face(verts, color, obj_id, i)
            self.faces.append(face)
            self.original_faces.append((verts, color, obj_id, i))
    
    def create_8_objects(self):
        """Создает 8 объектов для алгоритма Варнока"""
        
        # 8 объектов ближе к камере и центру
        positions = [
            Vector3D(-100, -100, 100),
            Vector3D(100, -100, 150),
            Vector3D(-100, 100, 200),
            Vector3D(100, 100, 50),
            Vector3D(-50, -50, 0),
            Vector3D(50, -50, 100),
            Vector3D(-50, 50, 150),
            Vector3D(50, 50, 80)
        ]
        
        sizes = [80, 60, 70, 50, 90, 40, 65, 55]
        
        # Создаем объекты
        for i in range(8):
            if i % 2 == 0:
                self.create_cube(positions[i], sizes[i], i)
            else:
                self.create_pyramid(positions[i], sizes[i], i)
    
    def get_transformed_faces(self):
        """Возвращает грани с учетом вращения и масштаба"""
        transformed_faces = []
        
        for original_verts, color, obj_id, face_id in self.original_faces:
            # Применяем преобразования к каждой вершине
            rotated_vertices = []
            for vertex in original_verts:
                # Масштабирование
                scaled = Vector3D(vertex.x * self.scale, 
                                 vertex.y * self.scale, 
                                 vertex.z * self.scale)
                
                # Вращение вокруг X
                if self.rotation_x != 0:
                    rotated_x = Matrix3D.multiply_vector(
                        Matrix3D.rotation_x(math.radians(self.rotation_x)), scaled)
                else:
                    rotated_x = scaled
                
                # Вращение вокруг Y
                if self.rotation_y != 0:
                    rotated_y = Matrix3D.multiply_vector(
                        Matrix3D.rotation_y(math.radians(self.rotation_y)), rotated_x)
                else:
                    rotated_y = rotated_x
                
                rotated_vertices.append(rotated_y)
            
            # Создаем новую грань с повернутыми вершинами
            new_face = Face(rotated_vertices, color, obj_id, face_id)
            transformed_faces.append(new_face)
        
        return transformed_faces

class Warnock3DApp:
    """Главное приложение"""
    def __init__(self, root):
        self.root = root
        self.root.title("3D Алгоритм Варнока - Вариант 4")
        self.root.geometry("1200x700")
        
        # Создаем 3D сцену
        self.scene = Scene3D()
        self.scene.create_8_objects()
        
        # Инициализируем алгоритм Варнока
        self.algorithm = Warnock3D()
        
        # Параметры окна - устанавливаем окно по центру
        self.window_size = 200
        self.window_x = 300 - self.window_size/2
        self.window_y = 300 - self.window_size/2
        
        # Создаем интерфейс
        self.create_interface()
        
        # Рисуем начальную сцену
        self.draw_scene()
    
    def create_interface(self):
        # Главный фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая часть - 3D вид
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Холст для 3D отображения
        self.canvas_3d = tk.Canvas(left_frame, width=600, height=600, 
                                  bg='white', highlightthickness=1, 
                                  highlightbackground="black")
        self.canvas_3d.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Правая часть - управление и информация
        right_frame = tk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Заголовок
        tk.Label(right_frame, text="3D АЛГОРИТМ ВАРНОКА", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(right_frame, text="Вариант 4: 8 объектов", 
                font=('Arial', 12)).pack(pady=5)
        
        # Управление масштабом (пункт 1в)
        scale_frame = tk.LabelFrame(right_frame, text="Масштаб сцены", padx=10, pady=10)
        scale_frame.pack(fill=tk.X, pady=10)
        
        self.scale_var = tk.DoubleVar(value=1.0)
        tk.Scale(scale_frame, from_=0.3, to=3.0, resolution=0.1,
                variable=self.scale_var, orient=tk.HORIZONTAL,
                command=self.update_scale).pack(fill=tk.X)
        
        # Управление вращением
        rotate_frame = tk.LabelFrame(right_frame, text="Вращение сцены", padx=10, pady=10)
        rotate_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(rotate_frame, text="Вращение X:").pack(anchor=tk.W)
        self.rotate_x_var = tk.DoubleVar(value=0)
        tk.Scale(rotate_frame, from_=-180, to=180, 
                variable=self.rotate_x_var, orient=tk.HORIZONTAL,
                command=self.update_rotation).pack(fill=tk.X)
        
        tk.Label(rotate_frame, text="Вращение Y:").pack(anchor=tk.W, pady=10)
        self.rotate_y_var = tk.DoubleVar(value=0)
        tk.Scale(rotate_frame, from_=-180, to=180,
                variable=self.rotate_y_var, orient=tk.HORIZONTAL,
                command=self.update_rotation).pack(fill=tk.X)
        
        # Управление окном (пункт 4б)
        window_frame = tk.LabelFrame(right_frame, text="Окно Варнока", padx=10, pady=10)
        window_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(window_frame, text="Размер окна:").pack(anchor=tk.W)
        self.window_size_var = tk.IntVar(value=self.window_size)
        tk.Scale(window_frame, from_=50, to=400,
                variable=self.window_size_var, orient=tk.HORIZONTAL,
                command=self.update_window_size).pack(fill=tk.X)
        
        tk.Label(window_frame, text="Позиция X:").pack(anchor=tk.W, pady=10)
        self.window_x_var = tk.IntVar(value=self.window_x)
        tk.Scale(window_frame, from_=50, to=550,
                variable=self.window_x_var, orient=tk.HORIZONTAL,
                command=self.update_window_pos).pack(fill=tk.X)
        
        tk.Label(window_frame, text="Позиция Y:").pack(anchor=tk.W, pady=10)
        self.window_y_var = tk.IntVar(value=self.window_y)
        tk.Scale(window_frame, from_=50, to=550,
                variable=self.window_y_var, orient=tk.HORIZONTAL,
                command=self.update_window_pos).pack(fill=tk.X)
        
        # Кнопки управления алгоритмом
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(button_frame, text="Запустить алгоритм", 
                 command=self.run_algorithm, width=20, bg='lightgreen').pack(pady=5)
        tk.Button(button_frame, text="Тест отображения", 
                 command=self.test_display, width=20).pack(pady=5)
        tk.Button(button_frame, text="Шаг алгоритма", 
                 command=self.next_step, width=20).pack(pady=5)
        tk.Button(button_frame, text="Сброс", 
                 command=self.reset, width=20).pack(pady=5)
        
        # Информация о цветах объектов
        info_frame = tk.LabelFrame(right_frame, text="Объекты", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        for i in range(8):
            color = self.scene.colors[i % len(self.scene.colors)]
            obj_type = "Куб" if i % 2 == 0 else "Пирамида"
            tk.Label(info_frame, text=f"Объект {i}: {obj_type}", 
                    fg=color, font=('Arial', 10)).pack(anchor=tk.W)
        
        # Лог алгоритма
        log_frame = tk.LabelFrame(right_frame, text="Лог алгоритма", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, width=40, height=15)
        scrollbar = tk.Scrollbar(log_frame)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def draw_scene(self):
        self.canvas_3d.delete("all")
        
        # Рисуем координатные оси
        self.draw_axes()
        
        # Рисуем масштабную сетку
        self.draw_grid()
        
        # Получаем трансформированные грани
        transformed_faces = self.scene.get_transformed_faces()
        
        # Рисуем все грани (wireframe)
        faces_drawn = 0
        for face in transformed_faces:
            projected = face.project_to_2d(self.scene.camera_pos)
            if projected:
                faces_drawn += 1
                # Рисуем контур грани
                for i in range(len(projected)):
                    x1, y1 = projected[i]
                    x2, y2 = projected[(i+1) % len(projected)]
                    self.canvas_3d.create_line(x1, y1, x2, y2, 
                                              fill=face.color, width=2)
        
        # Отладочная информация
        self.canvas_3d.create_text(300, 20, text=f"Отрисовано граней: {faces_drawn}", fill="black")
        
        # Рисуем окно Варнока
        self.draw_warnock_window()
    
    def test_display(self):
        """Тестирует отображение объектов"""
        self.log_text.delete(1.0, tk.END)
        transformed_faces = self.scene.get_transformed_faces()
        self.log_message("Тест отображения:")
        self.log_message(f"Всего граней: {len(transformed_faces)}")
        
        visible_count = 0
        for face in transformed_faces:
            projected = face.project_to_2d(self.scene.camera_pos)
            if projected:
                visible_count += 1
                self.log_message(f"  Грань {face.obj_id}-{face.face_id}: видима")
        
        self.log_message(f"Видимых граней: {visible_count}")
    
    def draw_axes(self):
        """Рисует 3D координатные оси"""
        # Ось X (красная)
        start = Vector3D(0, 0, 0)
        end_x = Vector3D(100, 0, 0)
        
        start_proj = self.project_point(start)
        end_x_proj = self.project_point(end_x)
        
        if start_proj and end_x_proj:
            self.canvas_3d.create_line(start_proj[0], start_proj[1], 
                                      end_x_proj[0], end_x_proj[1], 
                                      fill='red', width=3, arrow=tk.LAST)
            self.canvas_3d.create_text(end_x_proj[0]+10, end_x_proj[1], 
                                      text="X", fill='red', font=('Arial', 12, 'bold'))
        
        # Ось Y (зеленая)
        end_y = Vector3D(0, 100, 0)
        end_y_proj = self.project_point(end_y)
        
        if start_proj and end_y_proj:
            self.canvas_3d.create_line(start_proj[0], start_proj[1],
                                      end_y_proj[0], end_y_proj[1],
                                      fill='green', width=3, arrow=tk.LAST)
            self.canvas_3d.create_text(end_y_proj[0], end_y_proj[1]-10,
                                      text="Y", fill='green', font=('Arial', 12, 'bold'))
        
        # Ось Z (синяя)
        end_z = Vector3D(0, 0, 100)
        end_z_proj = self.project_point(end_z)
        
        if start_proj and end_z_proj:
            self.canvas_3d.create_line(start_proj[0], start_proj[1],
                                      end_z_proj[0], end_z_proj[1],
                                      fill='blue', width=3, arrow=tk.LAST)
            self.canvas_3d.create_text(end_z_proj[0]-10, end_z_proj[1],
                                      text="Z", fill='blue', font=('Arial', 12, 'bold'))
    
    def draw_grid(self):
        """Рисует масштабную сетку"""
        grid_color = '#e0e0e0'
        
        # Горизонтальные линии
        for i in range(-5, 6):
            y = 300 + i * 50
            self.canvas_3d.create_line(50, y, 550, y, fill=grid_color)
        
        # Вертикальные линии
        for i in range(-5, 6):
            x = 300 + i * 50
            self.canvas_3d.create_line(x, 50, x, 550, fill=grid_color)
    
    def draw_warnock_window(self):
        """Рисует окно для алгоритма Варнока"""
        x1, y1 = self.window_x, self.window_y
        x2, y2 = x1 + self.window_size, y1 + self.window_size
        
        # Рисуем окно
        self.canvas_3d.create_rectangle(x1, y1, x2, y2,
                                       outline='red', width=3, dash=(5, 5))
        
        # Если есть результаты разбиения, показываем их
        if hasattr(self, 'current_results'):
            for result in self.current_results:
                if 'window' in result and 'color' in result:
                    wx1, wy1, wx2, wy2 = result['window']
                    color = result['color']
                    if color != 'white':
                        # Полупрозрачная заливка
                        self.canvas_3d.create_rectangle(wx1, wy1, wx2, wy2,
                                                       fill=color, stipple='gray50',
                                                       outline='')
    
    def project_point(self, point):
        """Проецирует 3D точку на 2D"""
        # Применяем текущие преобразования
        scaled = Vector3D(point.x * self.scene.scale,
                         point.y * self.scene.scale,
                         point.z * self.scene.scale)
        
        # Вращение
        if self.scene.rotation_x != 0:
            rotated = Matrix3D.multiply_vector(
                Matrix3D.rotation_x(math.radians(self.scene.rotation_x)), scaled)
        else:
            rotated = scaled
        
        if self.scene.rotation_y != 0:
            rotated = Matrix3D.multiply_vector(
                Matrix3D.rotation_y(math.radians(self.scene.rotation_y)), rotated)
        
        # Проекция с перспективой
        dx = rotated.x - self.scene.camera_pos.x
        dy = rotated.y - self.scene.camera_pos.y
        dz = rotated.z - self.scene.camera_pos.z
        
        if dz <= 1:
            return None
        
        # Ортографическая проекция
        scale = 1.0
        x_proj = 300 + dx * scale * 2
        y_proj = 300 - dy * scale * 2
        
        return (x_proj, y_proj)
    
    def update_scale(self, value):
        self.scene.scale = float(value)
        self.draw_scene()
    
    def update_rotation(self, value):
        self.scene.rotation_x = self.rotate_x_var.get()
        self.scene.rotation_y = self.rotate_y_var.get()
        self.draw_scene()
    
    def update_window_size(self, value):
        self.window_size = int(value)
        self.window_size_var.set(self.window_size)
        self.draw_scene()
    
    def update_window_pos(self, value):
        self.window_x = self.window_x_var.get()
        self.window_y = self.window_y_var.get()
        self.draw_scene()
    
    def run_algorithm(self):
        """Запускает алгоритм Варнока"""
        self.log_text.delete(1.0, tk.END)
        self.algorithm.subdivisions = []
        
        # Определяем окно
        window = (self.window_x, self.window_y,
                 self.window_x + self.window_size,
                 self.window_y + self.window_size)
        
        # Получаем трансформированные грани
        transformed_faces = self.scene.get_transformed_faces()
        
        self.log_message("=== ЗАПУСК АЛГОРИТМА ВАРНОКА ===")
        self.log_message(f"Окно: x={window[0]:.1f}, y={window[1]:.1f}, " +
                        f"ширина={window[2]-window[0]:.1f}, высота={window[3]-window[1]:.1f}")
        self.log_message(f"Всего граней: {len(transformed_faces)}")
        
        # Проверяем, какие грани пересекают окно
        faces_in_window = []
        for face in transformed_faces:
            classification = self.algorithm.classify_face_vs_window(face, window, self.scene.camera_pos)
            if classification != "outside":
                faces_in_window.append(face)
                self.log_message(f"  Грань {face.obj_id}-{face.face_id}: {classification}")
        
        self.log_message(f"Граней в окне: {len(faces_in_window)}")
        
        if not faces_in_window:
            self.log_message("В окне нет граней!")
            return
        
        # Запускаем алгоритм
        self.log_message("\nНачинаем рекурсивное разбиение...")
        result = self.algorithm.subdivide(window, faces_in_window, self.scene.camera_pos)
        
        # Сохраняем результаты для отображения
        self.current_results = self.algorithm.subdivisions
        
        # Выводим статистику
        self.log_message(f"\n=== РЕЗУЛЬТАТ ===")
        self.log_message(f"Всего шагов разбиения: {len(self.algorithm.subdivisions)}")
        
        # Показываем глубину сравнения для выбранного окна
        self.show_depth_comparison(window, faces_in_window)
        
        # Перерисовываем сцену с результатами
        self.draw_scene()
        
        self.log_message("\nАлгоритм завершен успешно!")
    
    def show_depth_comparison(self, window, faces):
        """Показывает сравнение по глубине (пункт 4в)"""
        x1, y1, x2, y2 = window
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        self.log_message(f"\n=== СРАВНЕНИЕ ГЛУБИНЫ ===")
        self.log_message(f"Точка анализа: ({center_x:.1f}, {center_y:.1f})")
        
        # Находим все грани, которые содержат эту точку
        containing_faces = []
        
        for face in faces:
            bbox = face.get_bounding_box_2d(self.scene.camera_pos)
            if bbox:
                bx1, by1, bx2, by2 = bbox
                if bx1 <= center_x <= bx2 and by1 <= center_y <= by2:
                    # Вычисляем глубину в этой точке
                    depth = face.get_depth(center_x, center_y)
                    containing_faces.append((face, depth))
        
        # Сортируем по глубине (от ближних к дальним)
        containing_faces.sort(key=lambda x: x[1])
        
        if containing_faces:
            self.log_message(f"Найдено граней в точке: {len(containing_faces)}")
            for i, (face, depth) in enumerate(containing_faces):
                status = "ВИДИМ" if i == 0 else "скрыт"
                self.log_message(f"  {i+1}. Объект {face.obj_id} ({face.color}): " +
                               f"z={depth:.1f} ({status})")
        else:
            self.log_message("В этой точке нет граней")
    
    def next_step(self):
        """Выполняет следующий шаг алгоритма"""
        if not hasattr(self, 'current_results') or not self.current_results:
            self.log_message("Сначала запустите алгоритм!")
            return
        
        self.log_message(f"\n=== ШАГ {self.algorithm.current_step + 1} ===")
        
        if self.algorithm.current_step < len(self.current_results):
            step = self.current_results[self.algorithm.current_step]
            self.log_message(f"Окно: {step['window']}")
            self.log_message(f"Глубина рекурсии: {step['depth']}")
            self.log_message(f"Решение: {step.get('decision', 'Нет решения')}")
            self.log_message(f"Действие: {step.get('action', 'Нет действия')}")
            
            if step.get('color'):
                self.log_message(f"Цвет: {step['color']}")
            
            self.algorithm.current_step += 1
        else:
            self.log_message("Алгоритм завершен")
    
    def reset(self):
        """Сбрасывает состояние"""
        self.algorithm = Warnock3D()
        if hasattr(self, 'current_results'):
            del self.current_results
        
        self.log_text.delete(1.0, tk.END)
        self.draw_scene()
        self.log_message("Состояние сброшено")

def main():
    root = tk.Tk()
    app = Warnock3DApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()