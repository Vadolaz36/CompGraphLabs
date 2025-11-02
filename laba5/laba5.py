import math
import sys
import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ColorConversions:
    @staticmethod
    def rgb_to_hsv(r, g, b):
        r_n = r / 255.0
        g_n = g / 255.0
        b_n = b / 255.0

        max_val = max(r_n, g_n, b_n)
        min_val = min(r_n, g_n, b_n)
        delta = max_val - min_val

        if delta == 0:
            h = 0
        elif max_val == r_n:
            h = 60 * (((g_n - b_n) / delta) % 6)
        elif max_val == g_n:
            h = 60 * (((b_n - r_n) / delta) + 2)
        else:
            h = 60 * (((r_n - g_n) / delta) + 4)

        s = 0 if max_val == 0 else delta / max_val
        v = max_val

        return h, s, v

    @staticmethod
    def hsv_to_rgb(h, s, v):
        if s == 0:
            r = g = b = v
        else:
            h_i = (h / 60) % 6
            i = int(h_i)
            f = h_i - i

            p = v * (1 - s)
            q = v * (1 - f * s)
            t = v * (1 - (1 - f) * s)

            if i == 0:
                r, g, b = v, t, p
            elif i == 1:
                r, g, b = q, v, p
            elif i == 2:
                r, g, b = p, v, t
            elif i == 3:
                r, g, b = p, q, v
            elif i == 4:
                r, g, b = t, p, v
            else:
                r, g, b = v, p, q

        return int(r * 255), int(g * 255), int(b * 255)


class ImageProcessor:
    def __init__(self):
        self.image = None
        self.width = 0
        self.height = 0
        self.pixels = None
        self.original_image = None

    def load_image(self, filename):
        try:
            self.image = Image.open(filename).convert('RGB')
            self.original_image = self.image.copy()
            self.width, self.height = self.image.size
            self.pixels = self.image.load()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
            return False

    def save_image_ppm(self, filename):
        try:
            if self.image:
                # Убедимся, что расширение .ppm
                if not filename.lower().endswith('.ppm'):
                    filename += '.ppm'
                self.image.save(filename, 'PPM')
                return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения PPM: {e}")
        return False

    def get_image_for_display(self, max_size=(250, 250)):
        if not self.image:
            return None
        img = self.image.copy()
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def get_original_image_for_display(self, max_size=(250, 250)):
        if not self.original_image:
            return None
        img = self.original_image.copy()
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def maximize_saturation_contrast(self):
        if not self.image:
            return False

        result = Image.new('RGB', (self.width, self.height))
        result_pixels = result.load()

        min_saturation = 1.0
        max_saturation = 0.0

        for j in range(self.height):
            for i in range(self.width):
                r, g, b = self.pixels[i, j]
                h, s, v = ColorConversions.rgb_to_hsv(r, g, b)
                min_saturation = min(min_saturation, s)
                max_saturation = max(max_saturation, s)

        print(f"Диапазон насыщенности: {min_saturation:.3f} - {max_saturation:.3f}")

        for j in range(self.height):
            for i in range(self.width):
                r, g, b = self.pixels[i, j]
                h, s, v = ColorConversions.rgb_to_hsv(r, g, b)

                if max_saturation > min_saturation:
                    s_new = (s - min_saturation) / (max_saturation - min_saturation)
                else:
                    s_new = s

                s_new = min(1.0, s_new * 2.5)

                r_new, g_new, b_new = ColorConversions.hsv_to_rgb(h, s_new, v)
                result_pixels[i, j] = (r_new, g_new, b_new)

        self.image = result
        self.pixels = result_pixels
        return True

    def darken_blend(self, other_processor):
        if not self.image or not other_processor.image:
            return None

        width = min(self.width, other_processor.width)
        height = min(self.height, other_processor.height)

        result = Image.new('RGB', (width, height))
        result_pixels = result.load()

        for j in range(height):
            for i in range(width):
                r1, g1, b1 = self.pixels[i, j]
                r2, g2, b2 = other_processor.pixels[i, j]

                r_new = min(r1, r2)
                g_new = min(g1, g2)
                b_new = min(b1, b2)

                result_pixels[i, j] = (r_new, g_new, b_new)

        return result


class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений - Вариант 4")
        self.root.geometry("1100x900")

        self.processor1 = ImageProcessor()
        self.processor2 = ImageProcessor()
        self.blend_result = None

        self.original_img1_display = None
        self.processed_img1_display = None
        self.original_img2_display = None
        self.blend_result_display = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        img1_original_frame = ttk.LabelFrame(top_frame, text="Исходное изображение 1", padding="5")
        img1_original_frame.grid(row=0, column=0, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas_original1 = tk.Canvas(img1_original_frame, width=250, height=250, bg='white', relief='solid', bd=1)
        self.canvas_original1.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(img1_original_frame, text="Открыть PPM", command=self.open_image1).grid(row=1, column=0, pady=5)

        img1_processed_frame = ttk.LabelFrame(top_frame, text="Преобразованное изображение 1", padding="5")
        img1_processed_frame.grid(row=0, column=1, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas_processed1 = tk.Canvas(img1_processed_frame, width=250, height=250, bg='white', relief='solid',
                                           bd=1)
        self.canvas_processed1.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(img1_processed_frame, text="Увеличить насыщенность",
                   command=self.maximize_saturation).grid(row=1, column=0, pady=5)
        ttk.Button(img1_processed_frame, text="Сохранить PPM",
                   command=self.save_processed_image1).grid(row=2, column=0, pady=5)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        img2_original_frame = ttk.LabelFrame(bottom_frame, text="Исходное изображение 2", padding="5")
        img2_original_frame.grid(row=0, column=0, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas_original2 = tk.Canvas(img2_original_frame, width=250, height=250, bg='white', relief='solid', bd=1)
        self.canvas_original2.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(img2_original_frame, text="Открыть PPM", command=self.open_image2).grid(row=1, column=0, pady=5)

        blend_frame = ttk.LabelFrame(bottom_frame, text="Результат наложения", padding="5")
        blend_frame.grid(row=0, column=1, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas_blend = tk.Canvas(blend_frame, width=250, height=250, bg='white', relief='solid', bd=1)
        self.canvas_blend.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(blend_frame, text="Наложение",
                   command=self.apply_darken_blend).grid(row=1, column=0, pady=5)
        ttk.Button(blend_frame, text="Сохранить PPM",
                   command=self.save_blend_result).grid(row=2, column=0, pady=5)

        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Label(info_frame, text="Вариант 4: Увеличить контраст по насыщенности + Наложение",
                  font=('Arial', 10, 'bold')).grid(row=0, column=0, pady=5)

        ttk.Label(info_frame, text="Размер изображения 1:").grid(row=1, column=0, padx=10)
        self.size_label1 = ttk.Label(info_frame, text="0 x 0")
        self.size_label1.grid(row=1, column=1, padx=10)

        ttk.Label(info_frame, text="Размер изображения 2:").grid(row=1, column=2, padx=10)
        self.size_label2 = ttk.Label(info_frame, text="0 x 0")
        self.size_label2.grid(row=1, column=3, padx=10)

    def open_image1(self):
        filename = filedialog.askopenfilename(
            title="Открыть PPM изображение 1",
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")]
        )
        if filename and self.processor1.load_image(filename):
            self.display_original_image1()
            self.display_processed_image1()
            self.size_label1.config(text=f"{self.processor1.width} x {self.processor1.height}")

    def open_image2(self):
        filename = filedialog.askopenfilename(
            title="Открыть PPM изображение 2",
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")]
        )
        if filename and self.processor2.load_image(filename):
            self.display_original_image2()
            self.size_label2.config(text=f"{self.processor2.width} x {self.processor2.height}")

    def display_original_image1(self):
        if self.processor1.original_image:
            self.original_img1_display = self.processor1.get_original_image_for_display()
            self.canvas_original1.delete("all")
            self.canvas_original1.create_image(125, 125, image=self.original_img1_display)

    def display_processed_image1(self):
        if self.processor1.image:
            self.processed_img1_display = self.processor1.get_image_for_display()
            self.canvas_processed1.delete("all")
            self.canvas_processed1.create_image(125, 125, image=self.processed_img1_display)

    def display_original_image2(self):
        if self.processor2.original_image:
            self.original_img2_display = self.processor2.get_original_image_for_display()
            self.canvas_original2.delete("all")
            self.canvas_original2.create_image(125, 125, image=self.original_img2_display)

    def display_blend_result(self, image):
        if image:
            result_img = image.copy()
            result_img.thumbnail((250, 250), Image.Resampling.LANCZOS)
            self.blend_result_display = ImageTk.PhotoImage(result_img)
            self.canvas_blend.delete("all")
            self.canvas_blend.create_image(125, 125, image=self.blend_result_display)

    def maximize_saturation(self):
        if not self.processor1.image:
            messagebox.showwarning("Предупреждение", "Сначала откройте изображение 1")
            return

        if self.processor1.maximize_saturation_contrast():
            self.display_processed_image1()
            messagebox.showinfo("Успех", "Контраст по насыщенности увеличен")

    def apply_darken_blend(self):
        if not self.processor1.image or not self.processor2.image:
            messagebox.showwarning("Предупреждение", "Сначала откройте оба изображения")
            return

        self.blend_result = self.processor1.darken_blend(self.processor2)
        if self.blend_result:
            self.display_blend_result(self.blend_result)
            messagebox.showinfo("Успех", "Наложение с затемнением завершено")

    def save_processed_image1(self):
        if not self.processor1.image:
            messagebox.showwarning("Предупреждение", "Нет преобразованного изображения для сохранения")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить как PPM",
            defaultextension=".ppm",
            filetypes=[("PPM files", "*.ppm")]
        )
        if filename:
            if self.processor1.save_image_ppm(filename):
                messagebox.showinfo("Успех", "Преобразованное изображение сохранено как PPM")

    def save_blend_result(self):
        if not self.blend_result:
            messagebox.showwarning("Предупреждение", "Нет результата наложения для сохранения")
            return

        filename = filedialog.asksaveasfilename(
            title="Сохранить результат наложения как PPM",
            defaultextension=".ppm",
            filetypes=[("PPM files", "*.ppm")]
        )
        if filename:
            try:
                if not filename.lower().endswith('.ppm'):
                    filename += '.ppm'
                self.blend_result.save(filename, 'PPM')
                messagebox.showinfo("Успех", "Результат наложения сохранен как PPM")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")


def main():
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()