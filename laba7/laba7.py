import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageFilter


class ImageFilterLab:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №7 - Фильтрация изображений")
        self.root.geometry("1400x700")

        self.original_image = None
        self.result1_image = None
        self.result2_image = None
        self.result3_image = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        images_frame = ttk.Frame(main_frame)
        images_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        col1_frame = ttk.Frame(images_frame)
        col1_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.open_btn = ttk.Button(col1_frame, text="Открыть", command=self.open_image)
        self.open_btn.pack(pady=5)

        original_frame = ttk.LabelFrame(col1_frame, text="Оригинальное изображение", padding="5")
        original_frame.pack(fill=tk.BOTH, expand=True)

        self.original_label = ttk.Label(original_frame, text="Откройте изображение",
                                        background="white", anchor="center")
        self.original_label.pack(fill=tk.BOTH, expand=True)

        col2_frame = ttk.Frame(images_frame)
        col2_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.btn1 = ttk.Button(col2_frame, text="Уменьшение без ФНЧ", command=self.apply_reduction_without_filter)
        self.btn1.pack(pady=5)

        self.save_btn1 = ttk.Button(col2_frame, text="Сохранить", command=self.save_result1)
        self.save_btn1.pack(pady=2)

        result1_frame = ttk.LabelFrame(col2_frame, text="1. Уменьшение без ФНЧ", padding="5")
        result1_frame.pack(fill=tk.BOTH, expand=True)

        self.result1_label = ttk.Label(result1_frame, text="Каждый 2-й пиксель",
                                       background="white", anchor="center")
        self.result1_label.pack(fill=tk.BOTH, expand=True)

        col3_frame = ttk.Frame(images_frame)
        col3_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.btn2 = ttk.Button(col3_frame, text="Уменьшение с ФНЧ", command=self.apply_reduction_with_filter)
        self.btn2.pack(pady=5)

        self.save_btn2 = ttk.Button(col3_frame, text="Сохранить", command=self.save_result2)
        self.save_btn2.pack(pady=2)

        result2_frame = ttk.LabelFrame(col3_frame, text="2. Уменьшение с ФНЧ", padding="5")
        result2_frame.pack(fill=tk.BOTH, expand=True)

        self.result2_label = ttk.Label(result2_frame, text="ФНЧ + каждый 2-й пиксель",
                                       background="white", anchor="center")
        self.result2_label.pack(fill=tk.BOTH, expand=True)

        col4_frame = ttk.Frame(images_frame)
        col4_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.btn3 = ttk.Button(col4_frame, text="Комбинированный ФВЧ", command=self.apply_combined_high_pass)
        self.btn3.pack(pady=5)

        params_frame = ttk.Frame(col4_frame)
        params_frame.pack(pady=2)

        ttk.Label(params_frame, text="Порог:").pack(side=tk.LEFT)
        self.threshold_var = tk.StringVar(value="70")
        self.threshold_entry = ttk.Entry(params_frame, textvariable=self.threshold_var, width=5)
        self.threshold_entry.pack(side=tk.LEFT, padx=5)

        self.save_btn3 = ttk.Button(col4_frame, text="Сохранить", command=self.save_result3)
        self.save_btn3.pack(pady=2)

        result3_frame = ttk.LabelFrame(col4_frame, text="3. Комбинированный ФВЧ", padding="5")
        result3_frame.pack(fill=tk.BOTH, expand=True)

        self.result3_label = ttk.Label(result3_frame, text="Робертс слева + Прюитт справа",
                                       background="white", anchor="center")
        self.result3_label.pack(fill=tk.BOTH, expand=True)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )

        if file_path:
            try:
                self.original_image = Image.open(file_path)
                if self.original_image.mode != 'RGB':
                    self.original_image = self.original_image.convert('RGB')

                self.display_image(self.original_image, self.original_label)

                messagebox.showinfo("Успех", "Изображение успешно загружено")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")

    def display_image(self, image, label):
        if image is None:
            return

        w, h = image.size
        max_size = 350

        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))
            display_image = image.resize(new_size, Image.Resampling.LANCZOS)
        else:
            display_image = image

        photo = ImageTk.PhotoImage(display_image)
        label.configure(image=photo)
        label.image = photo

    def reduce_half(self, image):
        width, height = image.size
        new_width = width // 2
        new_height = height // 2

        new_image = Image.new('RGB', (new_width, new_height))

        for x in range(new_width):
            for y in range(new_height):
                pixel = image.getpixel((x * 2, y * 2))
                new_image.putpixel((x, y), pixel)

        return new_image

    def apply_threshold(self, image, threshold):
        if image.mode != 'RGB':
            image = image.convert('RGB')

        width, height = image.size
        result = Image.new('RGB', (width, height))

        threshold_value = int(threshold)

        for x in range(width):
            for y in range(height):
                r, g, b = image.getpixel((x, y))

                brightness = (r + g + b) // 3
                if brightness > threshold_value:
                    result.putpixel((x, y), (255, 255, 255))
                else:
                    result.putpixel((x, y), (0, 0, 0))

        return result

    def roberts_filter(self, image):
        if image.mode != 'RGB':
            image = image.convert('RGB')

        width, height = image.size
        result = Image.new('RGB', (width, height))

        for x in range(width - 1):
            for y in range(height - 1):
                p1 = image.getpixel((x, y))
                p2 = image.getpixel((x + 1, y))
                p3 = image.getpixel((x, y + 1))
                p4 = image.getpixel((x + 1, y + 1))

                r_grad = abs(p1[0] - p4[0]) + abs(p2[0] - p3[0])
                g_grad = abs(p1[1] - p4[1]) + abs(p2[1] - p3[1])
                b_grad = abs(p1[2] - p4[2]) + abs(p2[2] - p3[2])

                r_grad = min(255, int(r_grad))
                g_grad = min(255, int(g_grad))
                b_grad = min(255, int(b_grad))

                result.putpixel((x, y), (r_grad, g_grad, b_grad))

        return result

    def prewitt_filter(self, image):
        if image.mode != 'RGB':
            image = image.convert('RGB')

        width, height = image.size
        result = Image.new('RGB', (width, height))

        for x in range(1, width - 1):
            for y in range(1, height - 1):
                r_x, g_x, b_x = 0, 0, 0
                r_y, g_y, b_y = 0, 0, 0

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        px = x + i
                        py = y + j
                        r, g, b = image.getpixel((px, py))

                        if i == -1:
                            r_x -= r
                            g_x -= g
                            b_x -= b
                        elif i == 1:
                            r_x += r
                            g_x += g
                            b_x += b

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        px = x + i
                        py = y + j
                        r, g, b = image.getpixel((px, py))

                        if j == -1:
                            r_y -= r
                            g_y -= g
                            b_y -= b
                        elif j == 1:
                            r_y += r
                            g_y += g
                            b_y += b

                r_grad = min(255, abs(r_x) + abs(r_y))
                g_grad = min(255, abs(g_x) + abs(g_y))
                b_grad = min(255, abs(b_x) + abs(b_y))

                result.putpixel((x, y), (int(r_grad), int(g_grad), int(b_grad)))

        return result

    def apply_reduction_without_filter(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала откройте изображение")
            return

        try:
            self.result1_image = self.reduce_half(self.original_image)
            self.display_image(self.result1_image, self.result1_label)

            messagebox.showinfo("Успех", "Уменьшение без ФНЧ выполнено")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при уменьшении: {str(e)}")

    def apply_reduction_with_filter(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала откройте изображение")
            return

        try:
            blurred = self.original_image.filter(ImageFilter.GaussianBlur(2))
            self.result2_image = self.reduce_half(blurred)
            self.display_image(self.result2_image, self.result2_label)

            messagebox.showinfo("Успех", "Уменьшение с ФНЧ выполнено")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при уменьшении с ФНЧ: {str(e)}")

    def apply_combined_high_pass(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала откройте изображение")
            return

        try:
            threshold = int(self.threshold_var.get())
            if threshold < 0 or threshold > 255:
                messagebox.showwarning("Предупреждение", "Порог должен быть в диапазоне 0-255")
                return

            width, height = self.original_image.size
            half_width = width // 2

            combined_image = Image.new('RGB', (width, height))

            left_half = self.original_image.crop((0, 0, half_width, height))
            left_filtered = self.roberts_filter(left_half)
            left_thresholded = self.apply_threshold(left_filtered, threshold)
            combined_image.paste(left_thresholded, (0, 0))

            right_half = self.original_image.crop((half_width, 0, width, height))
            right_filtered = self.prewitt_filter(right_half)
            right_thresholded = self.apply_threshold(right_filtered, threshold)
            combined_image.paste(right_thresholded, (half_width, 0))

            self.result3_image = combined_image
            self.display_image(combined_image, self.result3_label)

            messagebox.showinfo("Успех", f"Комбинированный ФВЧ с порогом {threshold} выполнен")

        except ValueError:
            messagebox.showerror("Ошибка", "Порог должен быть целым числом")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при комбинированном ФВЧ: {str(e)}")

    def save_result1(self):
        if self.result1_image is None:
            messagebox.showwarning("Предупреждение", "Сначала примените уменьшение без ФНЧ")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить уменьшение без ФНЧ",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.result1_image.save(file_path)
                messagebox.showinfo("Успех", f"Результат сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

    def save_result2(self):
        if self.result2_image is None:
            messagebox.showwarning("Предупреждение", "Сначала примените уменьшение с ФНЧ")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить уменьшение с ФНЧ",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.result2_image.save(file_path)
                messagebox.showinfo("Успех", f"Результат сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")

    def save_result3(self):
        if self.result3_image is None:
            messagebox.showwarning("Предупреждение", "Сначала примените комбинированный ФВЧ")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить комбинированный ФВЧ",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.result3_image.save(file_path)
                messagebox.showinfo("Успех", f"Результат сохранен: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")


root = tk.Tk()
app = ImageFilterLab(root)
root.mainloop()