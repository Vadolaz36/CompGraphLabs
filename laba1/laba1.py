import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображения")
        self.root.geometry("800x600")

        self.image = None
        self.processed_image = None
        self.photo = None

        self.create_widgets()

    def create_widgets(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.load_btn = tk.Button(
            button_frame,
            text="Загрузить изображение",
            command=self.load_image,
            bg="white",
            font=("Times New Roman", 12)
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.process_btn = tk.Button(
            button_frame,
            text="Обработать изображение",
            command=self.process_image,
            bg="white",
            font=("Times New Roman", 12),
            state=tk.DISABLED
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = tk.Button(
            button_frame,
            text="Сохранить результат",
            command=self.save_image,
            bg="white",
            font=("Times New Roman", 12),
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.save_pbm_btn = tk.Button(
            button_frame,
            text="Сохранить как PBM",
            command=self.save_as_pbm,
            bg="white",
            font=("Times New Roman", 12),
            state=tk.DISABLED
        )
        self.save_pbm_btn.pack(side=tk.LEFT, padx=5)

        image_frame = tk.Frame(self.root)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.original_label = tk.Label(image_frame, text="Исходное изображение", font=("Times New Roman", 10))
        self.original_label.grid(row=0, column=0, pady=5)

        self.processed_label = tk.Label(image_frame, text="Обработанное изображение", font=("Times New Roman", 10))
        self.processed_label.grid(row=0, column=1, pady=5)

        self.original_Canvas = tk.Canvas(image_frame, width=350, height=350, bg="white", relief=tk.SUNKEN)
        self.original_Canvas.grid(row=1, column=0, padx=10)

        self.processed_Canvas = tk.Canvas(image_frame, width=350, height=350, bg="white", relief=tk.SUNKEN)
        self.processed_Canvas.grid(row=1, column=1, padx=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Все файлы", "*.*")
            ]
        )

        if file_path:
            try:
                self.image = Image.open(file_path).convert('RGB')
                self.processed_image = None
                self.display_image(self.image, self.original_Canvas)

                self.process_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.DISABLED)
                self.save_pbm_btn.config(state=tk.DISABLED)

                self.status_var.set(f"Загружено: {os.path.basename(file_path)} - {self.image.size[0]}x{self.image.size[1]}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")

    def process_image(self):
        if self.image:
            try:
                self.processed_image = self.image.copy()
                pixels = self.processed_image.load()
                width, height = self.processed_image.size

                pixels[0, 0] = (255, 127, 127)
                pixels[width // 2, 0] = (127, 255, 127)
                pixels[0, height - 1] = (127, 127, 255)

                self.display_image(self.processed_image, self.processed_Canvas)

                self.save_btn.config(state=tk.NORMAL)
                self.save_pbm_btn.config(state=tk.NORMAL)
                self.status_var.set("Изображение обработано - добавлены цветные точки")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обработки:\n{e}")

    def save_image(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(
                title="Сохранить изображение",
                defaultextension=".png",
                filetypes=[
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg"),
                    ("BMP", "*.bmp"),
                    ("Все файлы", "*.*")
                ]
            )

            if file_path:
                try:
                    self.processed_image.save(file_path)
                    self.status_var.set(f"Сохранено: {os.path.basename(file_path)}")
                    messagebox.showinfo("Успех", f"Изображение сохранено как:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{e}")

    def save_as_pbm(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(
                title="Сохранить как PBM",
                defaultextension=".pbm",
                filetypes=[("PBM", "*.pbm")]
            )

            if file_path:
                try:
                    self.save_pbm_binary(self.processed_image, file_path)
                    self.status_var.set(f"Сохранено PBM: {os.path.basename(file_path)}")
                    messagebox.showinfo("Успех", f"PBM файл сохранён как:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка сохранения PBM:\n{e}")

    def save_pbm_binary(self, image, output_path):
        bw_image = image.convert('1')
        width, height = bw_image.size

        with open(output_path, 'wb') as file:
            header = f"P4\n{width} {height}\n".encode('ascii')
            file.write(header)

            for y in range(height):
                byte = 0
                bit_count = 0

                for x in range(width):
                    pixel_value = 1 if bw_image.getpixel((x, y)) > 0 else 0
                    byte = (byte << 1) | pixel_value
                    bit_count += 1

                    if bit_count == 8 or x == width - 1:
                        if x == width - 1 and bit_count < 8:
                            byte = byte << (8 - bit_count)
                        file.write(bytes([byte]))
                        byte = 0
                        bit_count = 0

    def display_image(self, image, Canvas):
        width, height = image.size
        max_size = 350

        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
            display_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            display_image = image

        self.photo = ImageTk.PhotoImage(display_image)
        Canvas.delete("all")
        Canvas.create_image(175, 175, anchor=tk.CENTER, image=self.photo)

def main():
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()