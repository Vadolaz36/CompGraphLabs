import math
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import io

class PPMImage:
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height
        if width > 0 and height > 0:
            self.pixels = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]
        else:
            self.pixels = []
    
    def set_pixel(self, x, y, color):
        """Установка цвета пикселя"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
    
    def get_pixel(self, x, y):
        """Получение цвета пикселя"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return (255, 255, 255)  # Белый цвет для границ
    
    def save_ppm(self, filename):
        """Сохранение в формате PPM P3"""
        with open(filename, 'w') as f:
            # Заголовок PPM
            f.write(f"P3\n{self.width} {self.height}\n255\n")
            
            # Данные пикселей
            for y in range(self.height):
                line = []
                for x in range(self.width):
                    r, g, b = self.pixels[y][x]
                    line.extend([str(r), str(g), str(b)])
                f.write(" ".join(line) + "\n")
    
    def load_ppm(self, filename):
        """Загрузка из формата PPM P3"""
        with open(filename, 'r') as f:
            # Чтение заголовка
            magic_number = f.readline().strip()
            if magic_number != "P3":
                raise ValueError("Неверный формат PPM файла")
            
            # Пропускаем комментарии
            dimensions = f.readline().strip()
            while dimensions.startswith('#'):
                dimensions = f.readline().strip()
            
            # Размеры изображения
            width, height = map(int, dimensions.split())
            max_val = int(f.readline().strip())
            
            self.width = width
            self.height = height
            self.pixels = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
            
            # Чтение данных пикселей
            data = []
            for line in f:
                data.extend(line.split())
            
            index = 0
            for y in range(height):
                for x in range(width):
                    r = int(data[index])
                    g = int(data[index + 1])
                    b = int(data[index + 2])
                    self.set_pixel(x, y, (r, g, b))
                    index += 3
        return True
    
    @classmethod
    def from_pil_image(cls, pil_image):
        """Создание PPMImage из изображения PIL"""
        width, height = pil_image.size
        ppm_image = cls(width, height)
        
        # Конвертируем в RGB если нужно
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Копируем пиксели
        for y in range(height):
            for x in range(width):
                r, g, b = pil_image.getpixel((x, y))
                ppm_image.set_pixel(x, y, (r, g, b))
        
        return ppm_image
    
    def create_test_pattern(self):
        """Создание тестового изображения с паттернами"""
        for y in range(self.height):
            for x in range(self.width):
                # Цветовые градиенты
                r = (x * 255) // max(1, self.width - 1)
                g = (y * 255) // max(1, self.height - 1)
                b = ((x + y) * 255) // max(1, self.width + self.height - 2)
                
                # Шахматный паттерн для лучшей визуализации преобразований
                if (x // 30 + y // 30) % 2 == 0:
                    r = min(255, 255 - r)
                    g = min(255, 255 - g)
                    b = min(255, 255 - b)
                
                # Вертикальные линии
                if x % 40 == 0:
                    r, g, b = 255, 255, 255
                
                # Горизонтальные линии
                if y % 40 == 0:
                    r, g, b = 255, 255, 255
                
                self.set_pixel(x, y, (r, g, b))
    
    def to_pil_image(self):
        """Конвертация в изображение PIL для отображения в Tkinter"""
        image = Image.new("RGB", (self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                image.putpixel((x, y), self.pixels[y][x])
        return image

class ImageTransformerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Геометрические преобразования изображений - Вариант 4")
        self.root.geometry("1000x700")
        
        # Переменные для хранения изображений
        self.original_image = None
        self.affine_transformed = None
        self.affine_restored = None
        self.functional_transformed = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация весов строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Лабораторная работа №6. Геометрические преобразования\nВариант 4: Масштабирование, отражение, i = exp(x'), j = y'",
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Фрейм управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Кнопки управления
        ttk.Button(control_frame, text="Загрузить изображение", 
                  command=self.load_image).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Создать тестовое изображение", 
                  command=self.create_test_image).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Аффинное преобразование", 
                  command=self.apply_affine_transform).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(control_frame, text="Обратное аффинное преобразование", 
                  command=self.apply_inverse_affine).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(control_frame, text="Функциональное преобразование", 
                  command=self.apply_functional_transform).grid(row=0, column=4, padx=5, pady=5)
        
        # Параметры преобразований
        params_frame = ttk.LabelFrame(main_frame, text="Параметры преобразований", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(params_frame, text="Масштаб X:").grid(row=0, column=0, padx=5)
        self.scale_x_var = tk.DoubleVar(value=0.7)
        ttk.Scale(params_frame, from_=0.1, to=2.0, variable=self.scale_x_var, 
                 orient=tk.HORIZONTAL).grid(row=0, column=1, padx=5)
        ttk.Label(params_frame, textvariable=self.scale_x_var).grid(row=0, column=2, padx=5)
        
        ttk.Label(params_frame, text="Масштаб Y:").grid(row=0, column=3, padx=5)
        self.scale_y_var = tk.DoubleVar(value=0.7)
        ttk.Scale(params_frame, from_=0.1, to=2.0, variable=self.scale_y_var, 
                 orient=tk.HORIZONTAL).grid(row=0, column=4, padx=5)
        ttk.Label(params_frame, textvariable=self.scale_y_var).grid(row=0, column=5, padx=5)
        
        self.reflection_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Отражение", 
                       variable=self.reflection_var).grid(row=0, column=6, padx=10)
        
        # Фрейм для изображений
        images_frame = ttk.LabelFrame(main_frame, text="Изображения", padding="10")
        images_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(3, weight=1)
        
        # Создаем вкладки для изображений
        self.notebook = ttk.Notebook(images_frame)
        self.notebook.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        images_frame.columnconfigure(0, weight=1)
        images_frame.rowconfigure(0, weight=1)
        
        # Создаем вкладки
        self.tab_original = ttk.Frame(self.notebook)
        self.tab_affine = ttk.Frame(self.notebook)
        self.tab_restored = ttk.Frame(self.notebook)
        self.tab_functional = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_original, text="Исходное")
        self.notebook.add(self.tab_affine, text="Аффинное преобразование")
        self.notebook.add(self.tab_restored, text="Обратное аффинное")
        self.notebook.add(self.tab_functional, text="Функциональное преобразование")
        
        # Холсты для отображения изображений
        self.canvas_original = tk.Canvas(self.tab_original, bg="white", width=400, height=300)
        self.canvas_original.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self.canvas_affine = tk.Canvas(self.tab_affine, bg="white", width=400, height=300)
        self.canvas_affine.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self.canvas_restored = tk.Canvas(self.tab_restored, bg="white", width=400, height=300)
        self.canvas_restored.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self.canvas_functional = tk.Canvas(self.tab_functional, bg="white", width=400, height=300)
        self.canvas_functional.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Фрейм для сохранения
        save_frame = ttk.Frame(main_frame)
        save_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(save_frame, text="Сохранить все изображения (PPM)", 
                  command=self.save_all_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(save_frame, text="Сохранить текущее изображение (PPM)", 
                  command=self.save_current_image).pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def load_image(self):
        """Загрузка изображения в любом формате"""
        filename = filedialog.askopenfilename(
            title="Выберите файл изображения",
            filetypes=[
                ("Все изображения", "*.bmp *.jpg *.jpeg *.png *.gif *.tiff *.ppm"),
                ("BMP", "*.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("GIF", "*.gif"),
                ("TIFF", "*.tiff"),
                ("PPM", "*.ppm"),
                ("Все файлы", "*.*")
            ]
        )
        if filename:
            try:
                # Загружаем изображение с помощью PIL
                pil_image = Image.open(filename)
                
                # Конвертируем в PPMImage
                self.original_image = PPMImage.from_pil_image(pil_image)
                
                self.display_image(self.original_image, self.canvas_original)
                self.status_var.set(f"Изображение загружено: {filename} ({pil_image.size[0]}x{pil_image.size[1]})")
                messagebox.showinfo("Успех", f"Изображение загружено!\nРазмер: {pil_image.size[0]}x{pil_image.size[1]}\nФормат: {pil_image.format}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")
                self.status_var.set("Ошибка загрузки изображения")
    
    def create_test_image(self):
        """Создание тестового изображения"""
        try:
            self.original_image = PPMImage(400, 300)
            self.original_image.create_test_pattern()
            self.display_image(self.original_image, self.canvas_original)
            self.status_var.set("Тестовое изображение создано: 400x300 пикселей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать тестовое изображение: {str(e)}")
    
    def apply_affine_transform(self):
        """Применение аффинного преобразования"""
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите или создайте изображение")
            return
        
        try:
            self.affine_transformed = affine_transform(
                self.original_image, 
                self.scale_x_var.get(), 
                self.scale_y_var.get(), 
                self.reflection_var.get()
            )
            self.display_image(self.affine_transformed, self.canvas_affine)
            self.status_var.set("Аффинное преобразование применено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при аффинном преобразовании: {str(e)}")
    
    def apply_inverse_affine(self):
        """Применение обратного аффинного преобразования"""
        if self.affine_transformed is None:
            messagebox.showwarning("Предупреждение", "Сначала примените аффинное преобразование")
            return
        
        try:
            self.affine_restored = inverse_affine_transform(
                self.affine_transformed,
                self.original_image.width,
                self.original_image.height,
                self.scale_x_var.get(),
                self.scale_y_var.get(),
                self.reflection_var.get()
            )
            self.display_image(self.affine_restored, self.canvas_restored)
            self.status_var.set("Обратное аффинное преобразование применено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обратном аффинном преобразовании: {str(e)}")
    
    def apply_functional_transform(self):
        """Применение функционального преобразования"""
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите или создайте изображение")
            return
        
        try:
            self.functional_transformed = functional_transform(self.original_image)
            self.display_image(self.functional_transformed, self.canvas_functional)
            self.status_var.set("Функциональное преобразование применено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при функциональном преобразовании: {str(e)}")
    
    def display_image(self, ppm_image, canvas):
        """Отображение PPM изображения на холсте"""
        if ppm_image is None:
            return
        
        # Конвертируем в PIL Image
        pil_image = ppm_image.to_pil_image()
        
        # Получаем текущий размер холста
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400
            canvas_height = 300
        
        # Вычисляем соотношение сторон
        img_ratio = ppm_image.width / ppm_image.height
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            display_width = canvas_width
            display_height = int(canvas_width / img_ratio)
        else:
            display_height = canvas_height
            display_width = int(canvas_height * img_ratio)
        
        # Масштабируем изображение
        pil_image_resized = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # Конвертируем в PhotoImage для Tkinter
        self.tk_image = ImageTk.PhotoImage(pil_image_resized)
        
        # Очищаем холст и отображаем изображение
        canvas.delete("all")
        canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=self.tk_image)
    
    def save_all_images(self):
        """Сохранение всех изображений в формате PPM"""
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Нет изображений для сохранения")
            return
        
        directory = filedialog.askdirectory(title="Выберите папку для сохранения PPM файлов")
        if directory:
            try:
                if self.original_image:
                    self.original_image.save_ppm(os.path.join(directory, "original.ppm"))
                if self.affine_transformed:
                    self.affine_transformed.save_ppm(os.path.join(directory, "affine_transformed.ppm"))
                if self.affine_restored:
                    self.affine_restored.save_ppm(os.path.join(directory, "affine_restored.ppm"))
                if self.functional_transformed:
                    self.functional_transformed.save_ppm(os.path.join(directory, "functional_transformed.ppm"))
                
                self.status_var.set(f"PPM изображения сохранены в папку: {directory}")
                messagebox.showinfo("Успех", "Все изображения сохранены в формате PPM!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
    
    def save_current_image(self):
        """Сохранение текущего изображения в формате PPM"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
        image_map = {
            "Исходное": self.original_image,
            "Аффинное преобразование": self.affine_transformed,
            "Обратное аффинное": self.affine_restored,
            "Функциональное преобразование": self.functional_transformed
        }
        
        image_to_save = image_map.get(current_tab)
        
        if image_to_save is None:
            messagebox.showwarning("Предупреждение", "Нет изображения для сохранения")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Сохранить как PPM",
            defaultextension=".ppm",
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                image_to_save.save_ppm(filename)
                self.status_var.set(f"PPM изображение сохранено: {filename}")
                messagebox.showinfo("Успех", "Изображение сохранено в формате PPM!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

def affine_transform(image, scale_x=0.7, scale_y=0.7, reflection=True):
    """
    Аффинное преобразование: масштабирование и отражение
    Возвращает новое изображение
    """
    result = PPMImage(image.width, image.height)
    
    # Заполняем белым фоном
    for y in range(result.height):
        for x in range(result.width):
            result.set_pixel(x, y, (255, 255, 255))
    
    # Применяем обратное преобразование для избежания пропусков
    for y in range(result.height):
        for x in range(result.width):
            # Вычисляем координаты в исходном изображении
            if reflection:
                # Отражение по горизонтали + масштабирование
                orig_x = int((result.width - 1 - x) / scale_x)
            else:
                orig_x = int(x / scale_x)
            
            orig_y = int(y / scale_y)
            
            # Копируем пиксель, если координаты в пределах
            if 0 <= orig_x < image.width and 0 <= orig_y < image.height:
                color = image.get_pixel(orig_x, orig_y)
                result.set_pixel(x, y, color)
    
    return result

def inverse_affine_transform(transformed_image, original_width, original_height, scale_x=0.7, scale_y=0.7, reflection=True):
    """
    Обратное аффинное преобразование для восстановления изображения
    """
    result = PPMImage(original_width, original_height)
    
    # Заполняем белым фоном
    for y in range(result.height):
        for x in range(result.width):
            result.set_pixel(x, y, (255, 255, 255))
    
    # Применяем прямое преобразование
    for y in range(result.height):
        for x in range(result.width):
            if reflection:
                new_x = int(original_width - 1 - x * scale_x)
            else:
                new_x = int(x * scale_x)
            
            new_y = int(y * scale_y)
            
            if 0 <= new_x < transformed_image.width and 0 <= new_y < transformed_image.height:
                color = transformed_image.get_pixel(new_x, new_y)
                result.set_pixel(x, y, color)
    
    return result

def functional_transform(image):
    """
    Функциональное преобразование: i = exp(x'), j = y'
    Использует обратное преобразование для избежания пропусков
    """
    result = PPMImage(image.width, image.height)
    
    # Заполняем белым фоном
    for y in range(result.height):
        for x in range(result.width):
            result.set_pixel(x, y, (255, 255, 255))
    
    # Применяем обратное преобразование
    for y in range(result.height):
        for x in range(result.width):
            # Обратное преобразование: x' = ln(i)
            # Добавляем 1 чтобы избежать ln(0) и нормируем
            if x > 0:
                # Нормируем x в диапазон [1, e^2] для разумных значений
                norm_x = 1 + (x / result.width) * 3  # 3 ≈ ln(20) для ширины 400
                orig_x = int(math.log(norm_x) * result.width / 2)
            else:
                orig_x = 0
            
            orig_y = y
            
            # Копируем пиксель, если координаты в пределах
            if 0 <= orig_x < image.width and 0 <= orig_y < image.height:
                color = image.get_pixel(orig_x, orig_y)
                result.set_pixel(x, y, color)
    
    return result

def main():
    root = tk.Tk()
    app = ImageTransformerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()