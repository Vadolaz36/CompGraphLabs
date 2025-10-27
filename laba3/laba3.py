import tkinter as tk
from tkinter import messagebox, filedialog
from math import sqrt, floor
from PIL import Image, ImageDraw
import re


def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0


def DigitalDifferentialAnalyzer(x1, y1, x2, y2, Canvas, color):
    if abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1:
        Canvas.create_rectangle(x1, y1, x1 + 1, y1 + 1, fill=color, outline=color)
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
        Canvas.create_rectangle(floor(x), floor(y), floor(x) + 1, floor(y) + 1, fill=color, outline=color)
        x = x + dx
        y = y + dy


def BrezenhemFloat(x1, y1, x2, y2, Canvas, color):
    if abs(x1 - x2) < 0.1 and abs(y1 - y2) < 0.1:
        Canvas.create_rectangle(x1, y1, x1 + 1, y1 + 1, fill=color, outline=color)
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
        Canvas.create_rectangle(int(x), int(y), int(x) + 1, int(y) + 1, fill=color, outline=color)

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


def BrezenhemInteger(x1, y1, x2, y2, Canvas, color):
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))

    if x1 == x2 and y1 == y2:
        Canvas.create_rectangle(x1, y1, x1 + 1, y1 + 1, fill=color, outline=color)
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
        Canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline=color)

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


def DrawLineBuiltin(x1, y1, x2, y2, Canvas, color):
    Canvas.create_line(x1, y1, x2, y2, fill=color, width=1)


def DigitalDifferentialAnalyzer_pil(x1, y1, x2, y2, draw, color):
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


def BrezenhemFloat_pil(x1, y1, x2, y2, draw, color):
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


def BrezenhemInteger_pil(x1, y1, x2, y2, draw, color):
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


def DrawLineBuiltin_pil(x1, y1, x2, y2, draw, color):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)


current_segments = []
current_mode = "rhombus"


def ParseSvgFile(file_path):
    segments = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        line_pattern = r'<line[^>]*x1\s*=\s*["\']([^"\']*)["\'][^>]*y1\s*=\s*["\']([^"\']*)["\'][^>]*x2\s*=\s*["\']([^"\']*)["\'][^>]*y2\s*=\s*["\']([^"\']*)["\'][^>]*>'
        lines = re.findall(line_pattern, content, re.IGNORECASE)

        for line in lines:
            x1, y1, x2, y2 = map(float, line)
            segments.append((x1, y1, x2, y2))

        if not segments:
            path_pattern = r'<path[^>]*d\s*=\s*["\']([^"\']*)["\'][^>]*>'
            paths = re.findall(path_pattern, content, re.IGNORECASE)

            for path in paths:
                commands = re.findall(r'[MLml]\s*([\d\.]+)\s*([\d\.]+)', path)
                if len(commands) >= 2:
                    for i in range(len(commands) - 1):
                        x1, y1 = map(float, commands[i])
                        x2, y2 = map(float, commands[i + 1])
                        segments.append((x1, y1, x2, y2))

        return segments

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать SVG файл: {str(e)}")
        return []


def SaveAsPpm(image, file_path):
    try:
        width, height = image.size
        pixels = image.load()

        with open(file_path, 'w') as f:
            f.write("P3\n")
            f.write(f"# Created by Line Rasterization App\n")
            f.write(f"{width} {height}\n")
            f.write("255\n")

            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    f.write(f"{r} {g} {b} ")
                f.write("\n")

        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить PPM файл: {str(e)}")
        return False


def DrawSegmentsOnCanvas(segments, algorithm_func, color, offset_x=0, offset_y=0):
    for segment in segments:
        x1, y1, x2, y2 = segment
        shifted_x1 = x1 + offset_x
        shifted_y1 = y1 + offset_y
        shifted_x2 = x2 + offset_x
        shifted_y2 = y2 + offset_y
        algorithm_func(shifted_x1, shifted_y1, shifted_x2, shifted_y2, Canvas, color)


def DrawRhombusOnCanvas(x1, y1, x2, y2, other_diag_len, algorithm_func, color, offset_x=0, offset_y=0):
    shifted_x1 = x1 + offset_x
    shifted_y1 = y1 + offset_y
    shifted_x2 = x2 + offset_x
    shifted_y2 = y2 + offset_y

    center_x = (shifted_x1 + shifted_x2) / 2
    center_y = (shifted_y1 + shifted_y2) / 2

    dx = shifted_x2 - shifted_x1
    dy = shifted_y2 - shifted_y1
    diag1_len = sqrt(dx * dx + dy * dy)

    if diag1_len < 0.1:
        return

    perp_dx = -dy
    perp_dy = dx
    perp_len = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)

    if perp_len < 0.1:
        return

    perp_dx = perp_dx / perp_len * other_diag_len / 2
    perp_dy = perp_dy / perp_len * other_diag_len / 2

    x3 = center_x + perp_dx
    y3 = center_y + perp_dy
    x4 = center_x - perp_dx
    y4 = center_y - perp_dy

    algorithm_func(shifted_x1, shifted_y1, x3, y3, Canvas, color)
    algorithm_func(x3, y3, shifted_x2, shifted_y2, Canvas, color)
    algorithm_func(shifted_x2, shifted_y2, x4, y4, Canvas, color)
    algorithm_func(x4, y4, shifted_x1, shifted_y1, Canvas, color)


def LoadSvg():
    global current_segments, current_mode

    file_path = filedialog.askopenfilename(
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
    )

    if not file_path:
        return

    segments = ParseSvgFile(file_path)

    if not segments:
        messagebox.showwarning("Предупреждение", "Не удалось найти отрезки в SVG файле")
        return

    current_segments = segments
    current_mode = "svg"

    Canvas.delete("all")

    offsets = [(0, 0), (3, 0), (0, 3), (3, 3)]
    algorithms = [
        ("ЦДА", "blue", DigitalDifferentialAnalyzer),
        ("Брезенхем (вещ.)", "red", BrezenhemFloat),
        ("Брезенхем (цел.)", "green", BrezenhemInteger),
        ("Встроенный", "black", DrawLineBuiltin)
    ]

    for i, (offset_x, offset_y) in enumerate(offsets):
        algorithm_name, color, algorithm_func = algorithms[i]
        DrawSegmentsOnCanvas(segments, algorithm_func, color, offset_x, offset_y)
        Canvas.create_text(500, 20 + i * 20, text=algorithm_name, fill=color, font=("Arial", 10))


def CreateRhombus():
    global current_segments, current_mode

    try:
        x1 = float(entry_x1.get())
        y1 = float(entry_y1.get())
        x2 = float(entry_x2.get())
        y2 = float(entry_y2.get())
        other_diag_len = float(entry_len.get())

        if other_diag_len <= 0:
            messagebox.showerror("Ошибка", "Длина диагонали должна быть положительной")
            return

        current_segments = [(x1, y1, x2, y2, other_diag_len)]
        current_mode = "rhombus"

        Canvas.delete("all")

        offsets = [(0, 0), (3, 0), (0, 3), (3, 3)]
        algorithms = [
            ("ЦДА", "blue", DigitalDifferentialAnalyzer),
            ("Брезенхем (вещ.)", "red", BrezenhemFloat),
            ("Брезенхем (цел.)", "green", BrezenhemInteger),
            ("Встроенный", "black", DrawLineBuiltin)
        ]

        for i, (offset_x, offset_y) in enumerate(offsets):
            algorithm_name, color, algorithm_func = algorithms[i]
            DrawRhombusOnCanvas(x1, y1, x2, y2, other_diag_len, algorithm_func, color, offset_x, offset_y)
            Canvas.create_text(500, 20 + i * 20, text=algorithm_name, fill=color, font=("Arial", 10))

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")


def SaveToPpm():
    global current_segments, current_mode

    file_path = filedialog.asksaveasfilename(
        defaultextension=".ppm",
        filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")]
    )

    if not file_path:
        return

    try:
        image = Image.new('RGB', (600, 400), 'white')
        draw = ImageDraw.Draw(image)

        colors_ppm = [
            (0, 0, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 0)
        ]

        algorithms = [
            DigitalDifferentialAnalyzer_pil,
            BrezenhemFloat_pil,
            BrezenhemInteger_pil,
            DrawLineBuiltin_pil
        ]

        offsets = [(0, 0), (3, 0), (0, 3), (3, 3)]

        if current_mode == "rhombus" and current_segments:
            x1, y1, x2, y2, other_diag_len = current_segments[0]

            for i, (offset_x, offset_y) in enumerate(offsets):
                algorithm_func = algorithms[i]
                color = colors_ppm[i]
                DrawRhombusOnImage(image, draw, x1, y1, x2, y2, other_diag_len, algorithm_func, color, offset_x,
                                   offset_y)
#
        elif current_mode == "svg" and current_segments:
            for i, (offset_x, offset_y) in enumerate(offsets):
                algorithm_func = algorithms[i]
                color = colors_ppm[i]
                DrawSegmentsOnImage(image, draw, current_segments, algorithm_func, color, offset_x, offset_y)

        if SaveAsPpm(image, file_path):
            messagebox.showinfo("Успех", f"Изображение сохранено как {file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")


def DrawSegmentsOnImage(image, draw, segments, algorithm_func, color, offset_x=0, offset_y=0):
    for segment in segments:
        x1, y1, x2, y2 = segment
        shifted_x1 = x1 + offset_x
        shifted_y1 = y1 + offset_y
        shifted_x2 = x2 + offset_x
        shifted_y2 = y2 + offset_y
        algorithm_func(shifted_x1, shifted_y1, shifted_x2, shifted_y2, draw, color)


def DrawRhombusOnImage(image, draw, x1, y1, x2, y2, other_diag_len, algorithm_func, color, offset_x=0, offset_y=0):
    shifted_x1 = x1 + offset_x
    shifted_y1 = y1 + offset_y
    shifted_x2 = x2 + offset_x
    shifted_y2 = y2 + offset_y

    center_x = (shifted_x1 + shifted_x2) / 2
    center_y = (shifted_y1 + shifted_y2) / 2

    dx = shifted_x2 - shifted_x1
    dy = shifted_y2 - shifted_y1
    diag1_len = sqrt(dx * dx + dy * dy)

    if diag1_len < 0.1:
        return

    perp_dx = -dy
    perp_dy = dx
    perp_len = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)

    if perp_len < 0.1:
        return

    perp_dx = perp_dx / perp_len * other_diag_len / 2
    perp_dy = perp_dy / perp_len * other_diag_len / 2

    x3 = center_x + perp_dx
    y3 = center_y + perp_dy
    x4 = center_x - perp_dx
    y4 = center_y - perp_dy

    algorithm_func(shifted_x1, shifted_y1, x3, y3, draw, color)
    algorithm_func(x3, y3, shifted_x2, shifted_y2, draw, color)
    algorithm_func(shifted_x2, shifted_y2, x4, y4, draw, color)
    algorithm_func(x4, y4, shifted_x1, shifted_y1, draw, color)


root = tk.Tk()
root.title("Растеризация отрезков прямых")
root.geometry("600x500")

title_label = tk.Label(root, text="Растеризация отрезков прямых (вариант с ромбами)", font=("Arial", 14, "bold"))
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

btn_create = tk.Button(button_frame, text="Создать ромб", command=CreateRhombus, width=12, height=1)
btn_create.pack(side=tk.LEFT, padx=5)

btn_LoadSvg = tk.Button(button_frame, text="Загрузить SVG", command=LoadSvg, width=12, height=1)
btn_LoadSvg.pack(side=tk.LEFT, padx=5)

btn_save_ppm = tk.Button(button_frame, text="Сохранить PPM", command=SaveToPpm, width=12, height=1)
btn_save_ppm.pack(side=tk.LEFT, padx=5)

Canvas = tk.Canvas(root, width=600, height=400, bg="white", relief="solid", bd=1)
Canvas.pack(pady=10)

root.mainloop()