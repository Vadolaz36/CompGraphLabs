import tkinter as tk
from tkinter import ttk, filedialog
import math

class ImageInterpolationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Интерполяция изображений")
        self.root.geometry("900x600")
        
        self.image_data = None
        self.result_data = None
        self.width = 0
        self.height = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side="left", fill="y", padx=10)
        
        ttk.Label(control_frame, text="Интерполяция", font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Button(control_frame, text="Загрузить", command=self.load_image).pack(pady=5)
        ttk.Button(control_frame, text="Сохранить PPM", command=self.save_ppm).pack(pady=5)
        
        ttk.Label(control_frame, text="Метод:").pack(pady=5)
        self.interpolation_method = tk.StringVar(value="nearest")
        
        methods_frame = ttk.Frame(control_frame)
        methods_frame.pack(pady=5)
        
        methods = [("Ближайший", "nearest"), ("Билинейная", "bilinear"), ("Бикубическая", "bicubic")]
        
        for text, value in methods:
            rb = ttk.Radiobutton(methods_frame, text=text, variable=self.interpolation_method, value=value)
            rb.pack(anchor="w")
        
        ttk.Label(control_frame, text="Параметры:").pack(pady=(15,5))
        
        param_frame = ttk.Frame(control_frame)
        param_frame.pack(pady=5)
        
        ttk.Label(param_frame, text="Масштаб:").grid(row=0, column=0, sticky="w")
        self.scale_value = tk.DoubleVar(value=2.0)
        ttk.Scale(param_frame, from_=0.1, to=5.0, variable=self.scale_value, orient="horizontal", length=150).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(param_frame, textvariable=self.scale_value).grid(row=0, column=2)
        
        ttk.Label(param_frame, text="Угол:").grid(row=1, column=0, sticky="w")
        self.angle_value = tk.DoubleVar(value=30.0)
        ttk.Scale(param_frame, from_=-180.0, to=180.0, variable=self.angle_value, orient="horizontal", length=150).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(param_frame, textvariable=self.angle_value).grid(row=1, column=2)
        
        ttk.Label(param_frame, text="Скос X:").grid(row=2, column=0, sticky="w")
        self.skew_x_value = tk.DoubleVar(value=0.3)
        ttk.Scale(param_frame, from_=-1.0, to=1.0, variable=self.skew_x_value, orient="horizontal", length=150).grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(param_frame, textvariable=self.skew_x_value).grid(row=2, column=2)
        
        ttk.Label(param_frame, text="Скос Y:").grid(row=3, column=0, sticky="w")
        self.skew_y_value = tk.DoubleVar(value=0.3)
        ttk.Scale(param_frame, from_=-1.0, to=1.0, variable=self.skew_y_value, orient="horizontal", length=150).grid(row=3, column=1, padx=5, pady=2)
        ttk.Label(param_frame, textvariable=self.skew_y_value).grid(row=3, column=2)
        
        ttk.Label(control_frame, text="Преобразование:").pack(pady=5)
        self.transform_type = tk.StringVar(value="scale")
        
        transforms_frame = ttk.Frame(control_frame)
        transforms_frame.pack(pady=5)
        
        transforms = [("Масштаб", "scale"), ("Поворот", "rotate"), ("Скос", "skew")]
        
        for text, value in transforms:
            rb = ttk.Radiobutton(transforms_frame, text=text, variable=self.transform_type, value=value)
            rb.pack(anchor="w")
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Применить", command=self.apply_transform).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Сброс", command=self.reset_image).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Тест", command=self.create_test_image).pack(pady=5, fill="x")
        
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(side="right", fill="both", expand=True)
        
        self.canvas_original = tk.Canvas(image_frame, width=300, height=300, bg="white", borderwidth=2, relief="groove")
        self.canvas_original.pack(side="left", padx=10)
        self.canvas_result = tk.Canvas(image_frame, width=300, height=300, bg="white", borderwidth=2, relief="groove")
        self.canvas_result.pack(side="right", padx=10)
        
        ttk.Label(image_frame, text="Оригинал").place(x=110, y=310)
        ttk.Label(image_frame, text="Результат").place(x=420, y=310)
        
        self.info_label = ttk.Label(control_frame, text="Загрузите изображение")
        self.info_label.pack(pady=10)
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif *.ppm")]
        )
        
        if not file_path:
            return
        
        try:
            if file_path.lower().endswith('.ppm'):
                self.load_ppm(file_path)
            else:
                from PIL import Image
                img = Image.open(file_path).convert('RGB')
                self.width, self.height = img.size
                self.image_data = []
                for y in range(self.height):
                    row = []
                    for x in range(self.width):
                        r, g, b = img.getpixel((x, y))
                        row.append((r, g, b))
                    self.image_data.append(row)
                self.info_label.config(text=f"Загружено: {self.width}x{self.height}")
            
            self.result_data = [row[:] for row in self.image_data]
            self.draw_images()
            
        except ImportError:
            self.info_label.config(text="Установите Pillow: pip install pillow")
        except Exception as e:
            self.info_label.config(text=f"Ошибка: {str(e)}")
    
    def load_ppm(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        header = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            header.append(line)
            if len(header) == 3:
                break
        
        if len(header) < 3 or header[0] != 'P3':
            raise ValueError("Неверный формат PPM файла")
        
        self.width, self.height = map(int, header[1].split())
        
        pixel_values = []
        for line in lines[3:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            pixel_values.extend(map(int, line.split()))
        
        self.image_data = []
        idx = 0
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if idx + 2 < len(pixel_values):
                    r = pixel_values[idx]
                    g = pixel_values[idx + 1]
                    b = pixel_values[idx + 2]
                    row.append((r, g, b))
                    idx += 3
            self.image_data.append(row)
        
        self.info_label.config(text=f"Загружено PPM: {self.width}x{self.height}")
    
    def save_ppm(self):
        if not self.result_data:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ppm",
            filetypes=[("PPM файлы", "*.ppm")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                f.write("P3\n")
                f.write(f"{self.width} {self.height}\n")
                f.write("255\n")
                
                for y in range(self.height):
                    for x in range(self.width):
                        if y < len(self.result_data) and x < len(self.result_data[0]):
                            r, g, b = self.result_data[y][x]
                            f.write(f"{r} {g} {b} ")
                    f.write("\n")
            
            self.info_label.config(text=f"Сохранено: {file_path}")
            
        except Exception as e:
            self.info_label.config(text=f"Ошибка: {str(e)}")
    
    def draw_images(self):
        self.draw_image(self.image_data, self.canvas_original, "Оригинал")
        self.draw_image(self.result_data, self.canvas_result, "Результат")
    
    def draw_image(self, image_data, canvas, title=""):
        canvas.delete("all")
        
        if not image_data:
            return
        
        height = len(image_data)
        width = len(image_data[0]) if height > 0 else 0
        
        if width == 0 or height == 0:
            return
        
        scale = min(300/width, 300/height) * 0.8
        cell_size = max(1, int(scale))
        
        start_x = (300 - width * cell_size) // 2
        start_y = (300 - height * cell_size) // 2
        
        for y in range(height):
            if y >= len(image_data):
                continue
            for x in range(width):
                if x >= len(image_data[y]):
                    continue
                
                r, g, b = image_data[y][x]
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                color_str = f"#{r:02x}{g:02x}{b:02x}"
                
                canvas.create_rectangle(
                    start_x + x * cell_size,
                    start_y + y * cell_size,
                    start_x + (x + 1) * cell_size,
                    start_y + (y + 1) * cell_size,
                    fill=color_str,
                    outline=color_str
                )
        
        if title:
            canvas.create_text(150, 20, text=title, font=("Arial", 10, "bold"))
    
    def clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))
    
    def get_pixel(self, image, x, y):
        height = len(image)
        if height == 0:
            return (0, 0, 0)
        
        width = len(image[0])
        if width == 0:
            return (0, 0, 0)
        
        x = int(self.clamp(x, 0, width - 1))
        y = int(self.clamp(y, 0, height - 1))
        
        return image[y][x]
    
    def nearest_interpolation(self, image, x, y):
        x_near = round(x)
        y_near = round(y)
        return self.get_pixel(image, x_near, y_near)
    
    def bilinear_interpolation(self, image, x, y):
        l = math.floor(x)
        k = math.floor(y)
        a = x - l
        b = y - k
        
        try:
            f00 = self.get_pixel(image, l, k)
            f10 = self.get_pixel(image, l + 1, k)
            f01 = self.get_pixel(image, l, k + 1)
            f11 = self.get_pixel(image, l + 1, k + 1)
        except:
            return (0, 0, 0)
        
        result = [0, 0, 0]
        for i in range(3):
            value = ((1 - a) * (1 - b) * f00[i] + 
                    a * (1 - b) * f10[i] + 
                    (1 - a) * b * f01[i] + 
                    a * b * f11[i])
            result[i] = int(self.clamp(value, 0, 255))
        
        return tuple(result)
    
    def bicubic_interpolation(self, image, x, y):
        l = math.floor(x)
        k = math.floor(y)
        a = x - l
        b = y - k
        
        c1 = (a-1)*(a-2)*(a+1)*(b-1)*(b-2)*(b+1)/4
        c2 = -a*(a-2)*(a+1)*(b-1)*(b-2)*(b+1)/4
        c3 = b*(a-1)*(a-2)*(a+1)*(b-2)*(b+1)/4
        c4 = a*b*(a-2)*(a+1)*(b-2)*(b+1)/4
        c5 = -a*(a-1)*(a-2)*(b-1)*(b-2)*(b+1)/12
        c6 = -b*(a-1)*(a-2)*(a+1)*(b-1)*(b-2)/12
        c7 = a*b*(a-1)*(a-2)*(b-2)*(b+1)/12
        c8 = a*b*(a-2)*(a+1)*(b-1)*(b-2)/12
        c9 = a*(a-1)*(a+1)*(b-1)*(b-2)*(b+1)/12
        c10 = b*(a-1)*(a-2)*(a+1)*(b-1)*(b+1)/12
        c11 = a*b*(a-1)*(a-2)*(b-1)*(b-2)/36
        c12 = -a*b*(a-1)*(a+1)*(b-2)*(b+1)/12
        c13 = -a*b*(a-2)*(a+1)*(b-1)*(b+1)/12
        c14 = -a*b*(a-1)*(a+1)*(b-1)*(b-2)/36
        c15 = -a*b*(a-1)*(a-2)*(b-1)*(b+1)/36
        c16 = a*b*(a-1)*(a+1)*(b-1)*(b+1)/36
        
        pixels = [
            self.get_pixel(image, l, k),
            self.get_pixel(image, l, k+1),
            self.get_pixel(image, l+1, k),
            self.get_pixel(image, l+1, k+1),
            self.get_pixel(image, l, k-1),
            self.get_pixel(image, l-1, k),
            self.get_pixel(image, l+1, k-1),
            self.get_pixel(image, l-1, k+1),
            self.get_pixel(image, l, k+2),
            self.get_pixel(image, l+2, k),
            self.get_pixel(image, l-1, k-1),
            self.get_pixel(image, l+1, k+2),
            self.get_pixel(image, l+2, k+1),
            self.get_pixel(image, l-1, k+2),
            self.get_pixel(image, l+2, k-1),
            self.get_pixel(image, l+2, k+2)
        ]
        
        coeffs = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16]
        
        result = [0, 0, 0]
        for i in range(16):
            pixel = pixels[i]
            coeff = coeffs[i]
            for c in range(3):
                result[c] += coeff * pixel[c]
        
        for c in range(3):
            result[c] = int(self.clamp(result[c], 0, 255))
        
        return tuple(result)
    
    def apply_transform(self):
        if not self.image_data:
            return
        
        method = self.interpolation_method.get()
        transform_type = self.transform_type.get()
        
        width = self.width
        height = self.height
        
        new_image = []
        for y in range(height):
            row = []
            for x in range(width):
                if transform_type == "scale":
                    scale = self.scale_value.get()
                    src_x, src_y = self.scale_transform(x, y, width, height, scale)
                elif transform_type == "rotate":
                    angle = self.angle_value.get()
                    src_x, src_y = self.rotate_transform(x, y, width, height, angle)
                elif transform_type == "skew":
                    skew_x = self.skew_x_value.get()
                    skew_y = self.skew_y_value.get()
                    src_x, src_y = self.skew_transform(x, y, width, height, skew_x, skew_y)
                else:
                    src_x, src_y = x, y
                
                if method == "nearest":
                    color = self.nearest_interpolation(self.image_data, src_x, src_y)
                elif method == "bilinear":
                    color = self.bilinear_interpolation(self.image_data, src_x, src_y)
                elif method == "bicubic":
                    color = self.bicubic_interpolation(self.image_data, src_x, src_y)
                
                row.append(color)
            new_image.append(row)
        
        self.result_data = new_image
        self.draw_images()
    
    def scale_transform(self, x, y, width, height, scale):
        center_x = width / 2
        center_y = height / 2
        
        src_x = (x - center_x) / scale + center_x
        src_y = (y - center_y) / scale + center_y
        
        return src_x, src_y
    
    def rotate_transform(self, x, y, width, height, angle):
        center_x = width / 2
        center_y = height / 2
        
        angle_rad = math.radians(angle)
        
        dx = x - center_x
        dy = y - center_y
        
        cos_a = math.cos(-angle_rad)
        sin_a = math.sin(-angle_rad)
        
        src_x = dx * cos_a - dy * sin_a + center_x
        src_y = dx * sin_a + dy * cos_a + center_y
        
        return src_x, src_y
    
    def skew_transform(self, x, y, width, height, skew_x, skew_y):
        center_x = width / 2
        center_y = height / 2
        
        dx = x - center_x
        dy = y - center_y
        
        src_x = x - dy * skew_x
        src_y = y - dx * skew_y
        
        return src_x, src_y
    
    def reset_image(self):
        if self.image_data:
            self.result_data = [row[:] for row in self.image_data]
            self.draw_images()
    
    def create_test_image(self):
        self.width = 100
        self.height = 100
        self.image_data = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                r = int(255 * x / self.width)
                g = 100
                b = int(255 * y / self.height)
                row.append((r, g, b))
            self.image_data.append(row)
        
        self.result_data = [row[:] for row in self.image_data]
        self.draw_images()
        self.info_label.config(text=f"Тест: {self.width}x{self.height}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageInterpolationApp()
    app.run()