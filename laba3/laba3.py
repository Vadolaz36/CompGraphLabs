import tkinter as tk
from tkinter import messagebox, filedialog
from math import sqrt, floor
from PIL import Image, ImageDraw
import os

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def cda(x1, y1, x2, y2, canvas, color):
    if abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1:
        canvas.create_rectangle(x1, y1, x1+1, y1+1, fill=color, outline=color)
        return

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) >= abs(dy):
        l = abs(dx)
    else:
        l = abs(dy)

    if l < 0.1:
        return

    dx = dx / l
    dy = dy / l

    x = x1 + 0.5 * sign(dx)
    y = y1 + 0.5 * sign(dy)

    for i in range(int(l) + 1):
        canvas.create_rectangle(floor(x), floor(y), floor(x)+1, floor(y)+1, fill=color, outline=color)
        x = x + dx
        y = y + dy


def brezf(x1, y1, x2, y2, canvas, color):
    if abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1:
        canvas.create_rectangle(x1, y1, x1+1, y1+1, fill=color, outline=color)
        return

    sx = sign(x2 - x1)
    sy = sign(y2 - y1)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = x1
    y = y1
    flag = 0

    if dy > dx:
        temp = dx
        dx = dy
        dy = temp
        flag = 1

    if dx < 0.1:
        return

    f = dy / dx - 0.5

    steps = int(dx) + 1

    for i in range(steps):
        canvas.create_rectangle(int(x), int(y), int(x)+1, int(y)+1, fill=color, outline=color)

        if f >= 0:
            if flag == 1:
                x = x + sx
            else:
                y = y + sy
            f = f - 1

        if flag == 1:
            y = y + sy
        else:
            x = x + sx

        f = f + dy / dx


def brezi(x1, y1, x2, y2, canvas, color):
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))

    if x1 == x2 and y1 == y2:
        canvas.create_rectangle(x1, y1, x1+1, y1+1, fill=color, outline=color)
        return

    sx = sign(x2 - x1)
    sy = sign(y2 - y1)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = x1
    y = y1
    flag = 0

    if dy > dx:
        temp = dx
        dx = dy
        dy = temp
        flag = 1

    if dx == 0:
        return

    f = 2 * dy - dx

    for i in range(dx + 1):
        canvas.create_rectangle(x, y, x+1, y+1, fill=color, outline=color)

        if f >= 0:
            if flag == 1:
                x = x + sx
            else:
                y = y + sy
            f = f - 2 * dx

        if flag == 1:
            y = y + sy
        else:
            x = x + sx

        f = f + 2 * dy


def draw_line_builtin(x1, y1, x2, y2, canvas, color):
    canvas.create_line(x1, y1, x2, y2, fill=color, width=1)


def cda_pil(x1, y1, x2, y2, draw, color):
    if abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1:
        draw.point((x1, y1), fill=color)
        return

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) >= abs(dy):
        l = abs(dx)
    else:
        l = abs(dy)

    if l < 0.1:
        return

    dx = dx / l
    dy = dy / l

    x = x1 + 0.5 * sign(dx)
    y = y1 + 0.5 * sign(dy)

    for i in range(int(l) + 1):
        draw.point((floor(x), floor(y)), fill=color)
        x = x + dx
        y = y + dy


def brezf_pil(x1, y1, x2, y2, draw, color):
    if abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1:
        draw.point((x1, y1), fill=color)
        return

    sx = sign(x2 - x1)
    sy = sign(y2 - y1)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = x1
    y = y1
    flag = 0

    if dy > dx:
        temp = dx
        dx = dy
        dy = temp
        flag = 1

    if dx < 0.1:
        return

    f = dy / dx - 0.5

    steps = int(dx) + 1

    for i in range(steps):
        draw.point((int(x), int(y)), fill=color)

        if f >= 0:
            if flag == 1:
                x = x + sx
            else:
                y = y + sy
            f = f - 1

        if flag == 1:
            y = y + sy
        else:
            x = x + sx

        f = f + dy / dx


def brezi_pil(x1, y1, x2, y2, draw, color):
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))

    if x1 == x2 and y1 == y2:
        draw.point((x1, y1), fill=color)
        return

    sx = sign(x2 - x1)
    sy = sign(y2 - y1)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = x1
    y = y1
    flag = 0

    if dy > dx:
        temp = dx
        dx = dy
        dy = temp
        flag = 1

    if dx == 0:
        return

    f = 2 * dy - dx

    for i in range(dx + 1):
        draw.point((x, y), fill=color)

        if f >= 0:
            if flag == 1:
                x = x + sx
            else:
                y = y + sy
            f = f - 2 * dx

        if flag == 1:
            y = y + sy
        else:
            x = x + sx

        f = f + 2 * dy


def draw_line_builtin_pil(x1, y1, x2, y2, draw, color):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)


def create_rhombus():
    try:
        x1 = float(entry_x1.get())
        y1 = float(entry_y1.get())
        x2 = float(entry_x2.get())
        y2 = float(entry_y2.get())
        other_diag_len = float(entry_len.get())

        if other_diag_len <= 0:
            messagebox.showerror("Ошибка", "Длина диагонали должна быть положительной")
            return

        canvas.delete("all")

        offsets = [(0, 0), (3, 3), (6, 6), (9, 9)]
        algorithms = [
            ("ЦДА", "blue", cda),
            ("Брезенхем (вещ.)", "red", brezf),
            ("Брезенхем (цел.)", "green", brezi),
            ("Встроенный", "black", draw_line_builtin)
        ]

        for i, (offset_x, offset_y) in enumerate(offsets):
            algorithm_name, color, algorithm_func = algorithms[i]

            shifted_x1 = x1 + offset_x - 50
            shifted_y1 = y1 + offset_y - 30
            shifted_x2 = x2 + offset_x - 50
            shifted_y2 = y2 + offset_y - 30

            center_rhomb_x = (shifted_x1 + shifted_x2) / 2
            center_rhomb_y = (shifted_y1 + shifted_y2) / 2

            dx = shifted_x2 - shifted_x1
            dy = shifted_y2 - shifted_y1

            diag1_len = sqrt(dx * dx + dy * dy)

            if diag1_len < 0.1:
                continue

            perp_dx = -dy
            perp_dy = dx

            perp_len = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
            if perp_len < 0.1:
                continue

            perp_dx = perp_dx / perp_len * other_diag_len / 2
            perp_dy = perp_dy / perp_len * other_diag_len / 2

            x3 = center_rhomb_x + perp_dx
            y3 = center_rhomb_y + perp_dy
            x4 = center_rhomb_x - perp_dx
            y4 = center_rhomb_y - perp_dy

            algorithm_func(shifted_x1, shifted_y1, x3, y3, canvas, color)
            algorithm_func(x3, y3, shifted_x2, shifted_y2, canvas, color)
            algorithm_func(shifted_x2, shifted_y2, x4, y4, canvas, color)
            algorithm_func(x4, y4, shifted_x1, shifted_y1, canvas, color)

            canvas.create_text(250, 350 + i * 20, text=algorithm_name, fill=color, font=("Arial", 8))

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")


def save_image():
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if file_path:
            # Создаем изображение PIL
            image = Image.new('RGB', (600, 400), 'white')
            draw = ImageDraw.Draw(image)

            # Получаем параметры ромба
            x1 = float(entry_x1.get())
            y1 = float(entry_y1.get())
            x2 = float(entry_x2.get())
            y2 = float(entry_y2.get())
            other_diag_len = float(entry_len.get())

            colors_pil = {
                "blue": (0, 0, 255),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "black": (0, 0, 0)
            }

            algorithms_pil = [
                ("ЦДА", "blue", cda_pil),
                ("Брезенхем (вещ.)", "red", brezf_pil),
                ("Брезенхем (цел.)", "green", brezi_pil),
                ("Встроенный", "black", draw_line_builtin_pil)
            ]

            offsets = [(0, 0), (3, 3), (6, 6), (9, 9)]

            for i, (offset_x, offset_y) in enumerate(offsets):
                algorithm_name, color, algorithm_func = algorithms_pil[i]
                color_pil = colors_pil[color]

                shifted_x1 = x1 + offset_x - 50
                shifted_y1 = y1 + offset_y - 30
                shifted_x2 = x2 + offset_x - 50
                shifted_y2 = y2 + offset_y - 30

                center_rhomb_x = (shifted_x1 + shifted_x2) / 2
                center_rhomb_y = (shifted_y1 + shifted_y2) / 2
                dx = shifted_x2 - shifted_x1
                dy = shifted_y2 - shifted_y1
                diag1_len = sqrt(dx * dx + dy * dy)

                if diag1_len >= 0.1:
                    perp_dx = -dy
                    perp_dy = dx
                    perp_len = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)

                    if perp_len >= 0.1:
                        perp_dx = perp_dx / perp_len * other_diag_len / 2
                        perp_dy = perp_dy / perp_len * other_diag_len / 2

                        x3 = center_rhomb_x + perp_dx
                        y3 = center_rhomb_y + perp_dy
                        x4 = center_rhomb_x - perp_dx
                        y4 = center_rhomb_y - perp_dy

                        algorithm_func(shifted_x1, shifted_y1, x3, y3, draw, color_pil)
                        algorithm_func(x3, y3, shifted_x2, shifted_y2, draw, color_pil)
                        algorithm_func(shifted_x2, shifted_y2, x4, y4, draw, color_pil)
                        algorithm_func(x4, y4, shifted_x1, shifted_y1, draw, color_pil)

            image.save(file_path)
            messagebox.showinfo("Успех", f"Изображение сохранено как {file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")


root = tk.Tk()
root.title("Form1")
root.geometry("600x500")

title_label = tk.Label(root, text="Растеризация отрезков прямых", font=("Arial", 14, "bold"))
title_label.pack(pady=5)

input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="x1").grid(row=0, column=0, padx=5, sticky="e")
entry_x1 = tk.Entry(input_frame, width=8)
entry_x1.grid(row=0, column=1, padx=5)
entry_x1.insert(0, "200")

tk.Label(input_frame, text="y1").grid(row=0, column=2, padx=5, sticky="e")
entry_y1 = tk.Entry(input_frame, width=8)
entry_y1.grid(row=0, column=3, padx=5)
entry_y1.insert(0, "150")

tk.Label(input_frame, text="x2").grid(row=1, column=0, padx=5, sticky="e")
entry_x2 = tk.Entry(input_frame, width=8)
entry_x2.grid(row=1, column=1, padx=5)
entry_x2.insert(0, "400")

tk.Label(input_frame, text="y2").grid(row=1, column=2, padx=5, sticky="e")
entry_y2 = tk.Entry(input_frame, width=8)
entry_y2.grid(row=1, column=3, padx=5)
entry_y2.insert(0, "150")

tk.Label(input_frame, text="Длина второй диагонали").grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="e")
entry_len = tk.Entry(input_frame, width=8)
entry_len.grid(row=2, column=2, padx=5)
entry_len.insert(0, "200")

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_create = tk.Button(button_frame, text="Создать", command=create_rhombus,
                       width=10, height=1)
btn_create.pack(side=tk.LEFT, padx=10)

btn_save = tk.Button(button_frame, text="Сохранить", command=save_image,
                     width=10, height=1)
btn_save.pack(side=tk.LEFT, padx=10)

canvas = tk.Canvas(root, width=600, height=400, bg="white", relief="solid", bd=1)
canvas.pack(pady=10)

root.mainloop()