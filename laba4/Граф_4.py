import math
import tkinter as tk
from tkinter import ttk, messagebox

class CircleRasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №4 - Растеризация окружностей")
        self.root.geometry("900x700")
        
      
        self.image_width = 600
        self.image_height = 500
        self.pixels = [[0 for _ in range(self.image_width)] for _ in range(self.image_height)]
        
        self.setup_ui()
        
    def setup_ui(self):
       
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Лабораторная работа №4\nРастеризация окружностей", 
                               font=('Arial', 14, 'bold'),
                               justify=tk.CENTER)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Левая панель - управление
        control_frame = ttk.LabelFrame(main_frame, text="Параметры окружности", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Поля ввода
        ttk.Label(control_frame, text="Центр X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.center_x_entry = ttk.Entry(control_frame, width=10)
        self.center_x_entry.insert(0, "300")
        self.center_x_entry.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="Центр Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.center_y_entry = ttk.Entry(control_frame, width=10)
        self.center_y_entry.insert(0, "250")
        self.center_y_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(control_frame, text="Радиус R:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.radius_entry = ttk.Entry(control_frame, width=10)
        self.radius_entry.insert(0, "100")
        self.radius_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Кнопки алгоритмов
        algorithms_frame = ttk.LabelFrame(control_frame, text="Алгоритмы построения", padding="10")
        algorithms_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(algorithms_frame, 
                  text="По уравнению окружности", 
                  command=self.draw_by_equation).grid(row=0, column=0, sticky=tk.EW, pady=2)
        
        ttk.Button(algorithms_frame, 
                  text="По параметрическому уравнению", 
                  command=self.draw_by_parametric).grid(row=1, column=0, sticky=tk.EW, pady=2)
        
        ttk.Button(algorithms_frame, 
                  text="Алгоритм Брезенхема", 
                  command=self.draw_by_bresenham).grid(row=2, column=0, sticky=tk.EW, pady=2)
        
        ttk.Button(algorithms_frame, 
                  text="Встроенные средства", 
                  command=self.draw_builtin).grid(row=3, column=0, sticky=tk.EW, pady=2)
        
        # Кнопка создания арбелоса
        ttk.Button(control_frame, 
                  text="Создать арбелос (Вариант 4)", 
                  command=self.draw_arbelos).grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Кнопка очистки
        ttk.Button(control_frame, 
                  text="Очистить", 
                  command=self.clear_canvas).grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=2)
        
        # Кнопка сохранения
        ttk.Button(control_frame, 
                  text="Сохранить в PBM", 
                  command=self.save_to_pbm).grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=2)
        
        # Правая панель - холст
        canvas_frame = ttk.LabelFrame(main_frame, text="Результат", padding="10")
        canvas_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Холст для рисования
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.image_width, 
                               height=self.image_height,
                               bg="white",
                               relief=tk.SUNKEN,
                               borderwidth=2)
        self.canvas.pack(padx=5, pady=5)
        
        # Легенда
        legend_frame = ttk.Frame(canvas_frame)
        legend_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(legend_frame, text="Легенда:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(legend_frame, text="Уравнение - красный", foreground="red").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="Параметрич. - синий", foreground="blue").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="Брезенхем - зеленый", foreground="green").pack(side=tk.LEFT, padx=10)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        info_text = """Алгоритмы растеризации окружностей:
1. По уравнению: y = ±√(R² - x²)
2. Параметрический: x = R·cos(t), y = R·sin(t)  
3. Алгоритм Брезенхема - наиболее эффективный
4. Арбелос - геометрическая фигура из трех полуокружностей"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
    def get_circle_params(self):
        """Получение параметров окружности из полей ввода"""
        try:
            cx = int(self.center_x_entry.get())
            cy = int(self.center_y_entry.get())
            r = int(self.radius_entry.get())
            return cx, cy, r
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
            return None, None, None
    
    def draw_pixel(self, x, y, color="black"):
        """Рисование пикселя на холсте"""
        if 0 <= x < self.image_width and 0 <= y < self.image_height:
            self.canvas.create_rectangle(x, y, x+1, y+1, outline=color, fill=color)
            self.pixels[y][x] = 1
    
    def clear_canvas(self):
        """Очистка холста"""
        self.canvas.delete("all")
        self.pixels = [[0 for _ in range(self.image_width)] for _ in range(self.image_height)]
    
    def draw_by_equation(self):
        """Построение окружности по уравнению"""
        cx, cy, r = self.get_circle_params()
        if cx is None:
            return
        
        for x in range(r + 1):
            y = int(math.sqrt(r * r - x * x))
            # Рисуем во всех октантах
            self.draw_pixel(cx + x, cy + y, "red")
            self.draw_pixel(cx + x, cy - y, "red")
            self.draw_pixel(cx - x, cy + y, "red")
            self.draw_pixel(cx - x, cy - y, "red")
            self.draw_pixel(cx + y, cy + x, "red")
            self.draw_pixel(cx + y, cy - x, "red")
            self.draw_pixel(cx - y, cy + x, "red")
            self.draw_pixel(cx - y, cy - x, "red")
    
    def draw_by_parametric(self):
        """Построение окружности по параметрическому уравнению"""
        cx, cy, r = self.get_circle_params()
        if cx is None:
            return
        
        steps = int(2 * math.pi * r)
        for i in range(steps):
            t = 2 * math.pi * i / steps
            x = int(cx + r * math.cos(t))
            y = int(cy + r * math.sin(t))
            self.draw_pixel(x, y, "blue")
    
    def draw_by_bresenham(self):
        """Алгоритм Брезенхема для построения окружности"""
        cx, cy, r = self.get_circle_params()
        if cx is None:
            return
        
        x = 0
        y = r
        delta = 2 - 2 * r
        
        while y >= 0:
            self.draw_pixel(cx + x, cy + y, "green")
            self.draw_pixel(cx + x, cy - y, "green")
            self.draw_pixel(cx - x, cy + y, "green")
            self.draw_pixel(cx - x, cy - y, "green")
            
            if delta < 0:
                d1 = 2 * (delta + y) - 1
                if d1 <= 0:
                    x += 1
                    delta += 2 * x + 1
                else:
                    x += 1
                    y -= 1
                    delta += 2 * (x - y + 1)
            elif delta > 0:
                d2 = 2 * (delta - x) - 1
                if d2 <= 0:
                    x += 1
                    y -= 1
                    delta += 2 * (x - y + 1)
                else:
                    y -= 1
                    delta -= 2 * y + 1
            else:
                x += 1
                y -= 1
                delta += 2 * (x - y + 1)
    
    def draw_builtin(self):
        """Построение окружности встроенными средствами"""
        cx, cy, r = self.get_circle_params()
        if cx is None:
            return
        
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="black", width=1)
    
    def draw_arbelos(self):
        """Построение арбелоса (вариант 4)"""
        self.clear_canvas()
        
        # Параметры арбелоса
        base_y = 400
        left_x = 150
        right_x = 450
        center_x = 300
        
        # Радиусы полуокружностей
        big_radius = 150
        left_radius = 60
        right_radius = 90
        
        # Центры полуокружностей
        big_center = (center_x, base_y)
        left_center = (center_x - big_radius + left_radius, base_y)
        right_center = (center_x + big_radius - right_radius, base_y)
        
        # Рисуем базовую линию
        self.canvas.create_line(left_center[0] - left_radius, base_y, 
                               right_center[0] + right_radius, base_y, 
                               fill="black", width=2)
        
        # Большая полуокружность (алгоритм Брезенхема)
        for x in range(-big_radius, big_radius + 1):
            y = int(math.sqrt(big_radius * big_radius - x * x))
            if y >= 0:
                self.draw_pixel(big_center[0] + x, big_center[1] - y, "green")
        
        # Левая полуокружность (по уравнению)
        for x in range(-left_radius, left_radius + 1):
            y = int(math.sqrt(left_radius * left_radius - x * x))
            if y >= 0:
                self.draw_pixel(left_center[0] + x, left_center[1] - y, "red")
        
        # Правая полуокружность (параметрически)
        steps = int(2 * math.pi * right_radius)
        for i in range(steps // 2):
            t = math.pi * i / (steps // 2)
            x = int(right_center[0] + right_radius * math.cos(t))
            y = int(right_center[1] + right_radius * math.sin(t))
            if y <= right_center[1]:
                self.draw_pixel(x, y, "blue")
        
        # Подпись
        self.canvas.create_text(300, 50, text="Арбелос (Вариант 4)", 
                               font=('Arial', 12, 'bold'), fill="black")
    
    def save_to_pbm(self):
        """Сохранение изображения в PBM формате"""
        try:
            with open("output.pbm", "w") as f:
                f.write("P1\n")
                f.write(f"{self.image_width} {self.image_height}\n")
                for row in self.pixels:
                    f.write(" ".join(map(str, row)) + "\n")
            messagebox.showinfo("Успех", "Изображение сохранено в output.pbm")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

def main():
    root = tk.Tk()
    app = CircleRasterizationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()