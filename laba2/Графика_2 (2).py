import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import math

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 - Вариант 4")
        self.root.geometry("1000x700")
        
        # Переменные
        self.source_image = None
        self.result_image = None
        
        # Создание интерфейса
        self.create_interface()
    
    def create_interface(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление - Вариант 4", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Информация о варианте
        info_label = ttk.Label(control_frame, 
                              text="Фрагмент: КВАДРАТ из ЛЕВОГО НИЖНЕГО угла → в ПРАВЫЙ НИЖНИЙ угол | Функция: x*sin(x)",
                              font=("Arial", 10, "bold"))
        info_label.pack(pady=5)
        
        # Поля ввода параметров
        params_frame = ttk.Frame(control_frame)
        params_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(params_frame, text="Ширина нового изображения:").grid(row=0, column=0, padx=5, sticky="w")
        self.width_entry = ttk.Entry(params_frame, width=10)
        self.width_entry.insert(0, "600")
        self.width_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="Высота нового изображения:").grid(row=0, column=2, padx=5, sticky="w")
        self.height_entry = ttk.Entry(params_frame, width=10)
        self.height_entry.insert(0, "600")
        self.height_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(params_frame, text="Сторона квадрата:").grid(row=1, column=0, padx=5, sticky="w")
        self.square_size_entry = ttk.Entry(params_frame, width=10)
        self.square_size_entry.insert(0, "150")
        self.square_size_entry.grid(row=1, column=1, padx=5)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="1. Создать новое изображение", 
                  command=self.create_new_image).grid(row=0, column=0, padx=5, pady=2)
        
        ttk.Button(buttons_frame, text="2. Открыть исходное изображение", 
                  command=self.open_source_image).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(buttons_frame, text="3. Перенести квадратный фрагмент", 
                  command=self.transfer_square_fragment).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Button(buttons_frame, text="4. Нарисовать оси и график x*sin(x)", 
                  command=self.draw_axes_graph).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Button(buttons_frame, text="5. Сохранить результат в BMP", 
                  command=self.save_result).grid(row=0, column=4, padx=5, pady=2)
        
        # Области для изображений
        images_frame = ttk.LabelFrame(main_frame, text="Изображения", padding=10)
        images_frame.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для исходного изображения
        source_frame = ttk.Frame(images_frame)
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(source_frame, text="Исходное изображение", 
                 font=("Arial", 10, "bold")).pack(pady=5)
        
        # Canvas для исходного изображения с прокруткой
        source_canvas_frame = ttk.Frame(source_frame)
        source_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.source_canvas = tk.Canvas(source_canvas_frame, bg="lightgray", width=400, height=400)
        source_vscroll = ttk.Scrollbar(source_canvas_frame, orient=tk.VERTICAL, command=self.source_canvas.yview)
        source_hscroll = ttk.Scrollbar(source_canvas_frame, orient=tk.HORIZONTAL, command=self.source_canvas.xview)
        
        self.source_canvas.configure(yscrollcommand=source_vscroll.set, xscrollcommand=source_hscroll.set)
        
        source_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        source_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.source_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Фрейм для результата
        result_frame = ttk.Frame(images_frame)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(result_frame, text="Результат", 
                 font=("Arial", 10, "bold")).pack(pady=5)
        
        # Canvas для результата с прокруткой
        result_canvas_frame = ttk.Frame(result_frame)
        result_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_canvas = tk.Canvas(result_canvas_frame, bg="lightgray", width=400, height=400)
        result_vscroll = ttk.Scrollbar(result_canvas_frame, orient=tk.VERTICAL, command=self.result_canvas.yview)
        result_hscroll = ttk.Scrollbar(result_canvas_frame, orient=tk.HORIZONTAL, command=self.result_canvas.xview)
        
        self.result_canvas.configure(yscrollcommand=result_vscroll.set, xscrollcommand=result_hscroll.set)
        
        result_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        result_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding=5)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, text="Готов к работе. Создайте новое изображение и загрузите исходное.")
        self.info_label.pack()
    
    def create_new_image(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            
            if width <= 0 or height <= 0:
                messagebox.showerror("Ошибка", "Размеры изображения должны быть положительными числами")
                return
            
            self.result_image = Image.new('RGB', (width, height), 'white')
            self.update_result_display()
            self.info_label.config(text=f"Создано новое изображение {width}x{height} пикселей")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные размеры изображения")
    
    def open_source_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите исходное изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if file_path:
            try:
                self.source_image = Image.open(file_path).convert('RGB')
                self.update_source_display()
                self.info_label.config(text=f"Загружено изображение: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")
    
    def transfer_square_fragment(self):
        if self.source_image is None or self.result_image is None:
            messagebox.showerror("Ошибка", "Сначала создайте новое изображение и загрузите исходное")
            return
        
        try:
            square_size = int(self.square_size_entry.get())
            if square_size <= 0:
                messagebox.showerror("Ошибка", "Сторона квадрата должна быть положительным числом")
                return
                
            src_width, src_height = self.source_image.size
            res_width, res_height = self.result_image.size
            
            # Проверяем, что квадрат помещается в исходное изображение
            if square_size > min(src_width, src_height):
                messagebox.showerror("Ошибка", "Квадрат слишком большой для исходного изображения")
                return
            
            # ЛЕВЫЙ НИЖНИЙ угол исходного изображения
            src_x1 = 0  # левый верхний угол квадрата (X) - ЛЕВЫЙ край
            src_y1 = src_height - square_size  # левый верхний угол квадрата (Y) - НИЖНИЙ край
            src_x2 = square_size - 1  # правый нижний угол квадрата (X)
            src_y2 = src_height - 1  # правый нижний угол квадрата (Y)
            
            # Правый нижний угол нового изображения
            res_x1 = res_width - square_size  # левый верхний угол квадрата (X)
            res_y1 = res_height - square_size  # левый верхний угол квадрата (Y)
            res_x2 = res_width - 1  # правый нижний угол квадрата (X)
            res_y2 = res_height - 1  # правый нижний угол квадрата (Y)
            
            # Создаем копию результата для работы
            result_img = self.result_image.copy()
            
            # Копирование квадратного фрагмента
            for y in range(square_size):
                for x in range(square_size):
                    # Координаты в исходном изображении (ЛЕВЫЙ нижний угол)
                    src_x = src_x1 + x
                    src_y = src_y1 + y
                    
                    # Координаты в новом изображении (ПРАВЫЙ нижний угол)
                    res_x = res_x1 + x
                    res_y = res_y1 + y
                    
                    # Проверяем границы
                    if (0 <= src_x < src_width and 0 <= src_y < src_height and
                        0 <= res_x < res_width and 0 <= res_y < res_height):
                        pixel = self.source_image.getpixel((src_x, src_y))
                        result_img.putpixel((res_x, res_y), pixel)
            
            # Рисуем красную границу вокруг квадрата
            draw = ImageDraw.Draw(result_img)
            draw.rectangle([res_x1, res_y1, res_x2, res_y2], outline=(255, 0, 0), width=2)
            
            # Также рисуем границу на исходном изображении для наглядности
            self.source_image_with_border = self.source_image.copy()
            source_draw = ImageDraw.Draw(self.source_image_with_border)
            source_draw.rectangle([src_x1, src_y1, src_x2, src_y2], outline=(255, 0, 0), width=2)
            
            self.result_image = result_img
            self.update_result_display()
            self.update_source_display()  # Обновляем исходное изображение с границей
            self.info_label.config(text=f"Квадратный фрагмент {square_size}x{square_size} перенесен из левого нижнего в правый нижний угол")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный размер стороны квадрата")
    
    def draw_axes_graph(self):
        if self.result_image is None:
            messagebox.showerror("Ошибка", "Сначала создайте новое изображение")
            return
        
        result_img = self.result_image.copy()
        draw = ImageDraw.Draw(result_img)
        width, height = result_img.size
        
        # Рисование осей координат
        center_x = width // 4  # Смещаем график левее
        center_y = height // 2
        
        # Ось X
        draw.line([(50, center_y), (width-50, center_y)], fill=(0, 0, 0), width=2)
        # Ось Y
        draw.line([(center_x, 50), (center_x, height-50)], fill=(0, 0, 0), width=2)
        
        # Стрелки осей
        draw.line([(width-50, center_y), (width-60, center_y-5)], fill=(0, 0, 0), width=2)
        draw.line([(width-50, center_y), (width-60, center_y+5)], fill=(0, 0, 0), width=2)
        draw.line([(center_x, 50), (center_x-5, 60)], fill=(0, 0, 0), width=2)
        draw.line([(center_x, 50), (center_x+5, 60)], fill=(0, 0, 0), width=2)
        
        # Подписи осей
        draw.text((width-40, center_y-20), "X", fill=(0, 0, 0))
        draw.text((center_x+10, 40), "Y", fill=(0, 0, 0))
        
        # Деления на осях
        for i in range(0, width, 50):
            if i > 50 and i < width-50:
                draw.line([(i, center_y-3), (i, center_y+3)], fill=(0, 0, 0), width=1)
                if i % 100 == 0:  # Подписи каждые 100 пикселей
                    draw.text((i-10, center_y+10), str((i-center_x)//20), fill=(0, 0, 0))
        
        for i in range(0, height, 50):
            if i > 50 and i < height-50:
                draw.line([(center_x-3, i), (center_x+3, i)], fill=(0, 0, 0), width=1)
                if i % 100 == 0:  # Подписи каждые 100 пикселей
                    draw.text((center_x+10, i-10), str((center_y-i)//30), fill=(0, 0, 0))
        
        # Рисование графика функции x*sin(x) - вариант 4
        points = []
        scale_x = 20  # Масштаб по X
        scale_y = 30  # Масштаб по Y
        
        # Рисуем график для положительных x
        for i in range(1, (width - center_x - 50) * 10 // scale_x):
            x = i / 10.0
            try:
                y = x * math.sin(x)  # Функция для варианта 4: x*sin(x)
                pixel_x = center_x + int(x * scale_x)
                pixel_y = center_y - int(y * scale_y)
                
                if 0 <= pixel_x < width and 0 <= pixel_y < height:
                    points.append((pixel_x, pixel_y))
            except:
                continue
        
        # Рисуем график синей линией
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=(0, 0, 255), width=3)
        
        # Подпись графика
        draw.text((center_x + 100, 100), "y = x*sin(x)", fill=(0, 0, 255), font=None)
        
        self.result_image = result_img
        self.update_result_display()
        self.info_label.config(text="Оси координат и график функции x*sin(x) нарисованы")
    
    def save_result(self):
        if self.result_image is None:
            messagebox.showerror("Ошибка", "Нет изображения для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить результат в формате BMP",
            defaultextension=".bmp",
            filetypes=[("BMP files", "*.bmp")]
        )
        
        if file_path:
            try:
                # Сохраняем в формате BMP
                self.result_image.save(file_path, format='BMP')
                messagebox.showinfo("Успех", f"Изображение сохранено как {file_path}")
                self.info_label.config(text=f"Изображение сохранено в формате BMP: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def update_source_display(self):
        if self.source_image:
            display_size = 400
            # Используем изображение с границей, если оно есть
            if hasattr(self, 'source_image_with_border'):
                display_image = self.source_image_with_border.copy()
            else:
                display_image = self.source_image.copy()
            
            # Масштабируем для отображения с сохранением пропорций
            ratio = min(display_size/display_image.width, display_size/display_image.height)
            new_size = (int(display_image.width * ratio), int(display_image.height * ratio))
            display_image = display_image.resize(new_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_image)
            
            # Очищаем canvas и добавляем изображение
            self.source_canvas.delete("all")
            self.source_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.source_canvas.image = photo  # Сохраняем ссылку
            
            # Настраиваем прокрутку
            self.source_canvas.configure(scrollregion=self.source_canvas.bbox("all"))
    
    def update_result_display(self):
        if self.result_image:
            display_size = 400
            display_image = self.result_image.copy()
            
            # Масштабируем для отображения с сохранением пропорций
            ratio = min(display_size/display_image.width, display_size/display_image.height)
            new_size = (int(display_image.width * ratio), int(display_image.height * ratio))
            display_image = display_image.resize(new_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_image)
            
            # Очищаем canvas и добавляем изображение
            self.result_canvas.delete("all")
            self.result_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.result_canvas.image = photo  # Сохраняем ссылку
            
            # Настраиваем прокрутку
            self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()