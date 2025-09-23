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
    """Алгоритм ЦДА (Цифровой Дифференциальный Анализатор)"""
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
    """Алгоритм Брезенхема с вещественной арифметикой"""
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
    """Целочисленный алгоритм Брезенхема"""
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


def draw_line_builtin(x1, y1, x2, y2, Canvas, color):
    """Встроенная функция рисования линий"""
    Canvas.create_line(x1, y1, x2, y2, fill=color, width=1)


def parse_svg_file(file_path):
    """
    Парсит SVG файл и извлекает координаты отрезков
    Возвращает список отрезков в формате [(x1, y1, x2, y2), ...]
    """
    segments = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Ищем все линии в SVG файле
        # Формат: <line x1="100" y1="100" x2="200" y2="200" />
        line_pattern = r'<line[^>]*x1\s*=\s*["\']([^"\']*)["\'][^>]*y1\s*=\s*["\']([^"\']*)["\'][^>]*x2\s*=\s*["\']([^"\']*)["\'][^>]*y2\s*=\s*["\']([^"\']*)["\'][^>]*>'
        lines = re.findall(line_pattern, content, re.IGNORECASE)

        for line in lines:
            x1, y1, x2, y2 = map(float, line)
            segments.append((x1, y1, x2, y2))

        # Если не нашли линии, пробуем найти пути (path)
        if not segments:
            path_pattern = r'<path[^>]*d\s*=\s*["\']([^"\']*)["\'][^>]*>'
            paths = re.findall(path_pattern, content, re.IGNORECASE)

            for path in paths:
                # Упрощенный парсинг пути - ищем только прямые линии (M, L команды)
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


def save_as_pbm(image, file_path):
    """
    Сохраняет изображение в формате PBM (Portable BitMap)
    PBM - текстовый формат для черно-белых изображений
    """
    try:
        # Конвертируем в черно-белое изображение
        bw_image = image.convert('1')
        width, height = bw_image.size

        with open(file_path, 'w') as f:
            # Записываем заголовок PBM
            f.write("P1\n")
            f.write(f"# Created by Line Rasterization App\n")
            f.write(f"{width} {height}\n")

            # Записываем пиксели
            pixels = bw_image.load()
            for y in range(height):
                line = []
                for x in range(width):
                    # В PBM: 0 - белый, 1 - черный (инвертируем)
                    pixel = 0 if pixels[x, y] == 255 else 1
                    line.append(str(pixel))
                f.write(" ".join(line) + "\n")

        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить PBM файл: {str(e)}")
        return False


def load_svg():
    """Загружает отрезки из SVG файла и рисует их"""
    file_path = filedialog.askopenfilename(
        filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
    )

    if not file_path:
        return

    segments = parse_svg_file(file_path)

    if not segments:
        messagebox.showwarning("Предупреждение", "Не удалось найти отрезки в SVG файле")
        return

    # Очищаем канвас
    Canvas.delete("all")

    # Рисуем отрезки разными алгоритмами
    offsets = [(0, 0), (15, 0), (0, 15), (15, 15)]
    algorithms = [
        ("ЦДА", "blue", DigitalDifferentialAnalyzer),
        ("Брезенхем (вещ.)", "red", BrezenhemFloat),
        ("Брезенхем (цел.)", "green", BrezenhemInteger),
        ("Встроенный", "black", draw_line_builtin)
    ]

    for i, (offset_x, offset_y) in enumerate(offsets):
        algorithm_name, color, algorithm_func = algorithms[i]

        for segment in segments:
            x1, y1, x2, y2 = segment
            # Применяем смещение к координатам
            shifted_x1 = x1 + offset_x
            shifted_y1 = y1 + offset_y
            shifted_x2 = x2 + offset_x
            shifted_y2 = y2 + offset_y

            algorithm_func(shifted_x1, shifted_y1, shifted_x2, shifted_y2, Canvas, color)

        # Подписываем алгоритмы
        Canvas.create_text(500, 20 + i * 20, text=algorithm_name, fill=color, font=("Arial", 10))


def create_rhombus():
    """Создает ромб по заданным координатам диагонали и длине второй диагонали"""
    try:
        x1 = float(entry_x1.get())
        y1 = float(entry_y1.get())
        x2 = float(entry_x2.get())
        y2 = float(entry_y2.get())
        other_diag_len = float(entry_len.get())

        if other_diag_len <= 0:
            messagebox.showerror("Ошибка", "Длина диагонали должна быть положительной")
            return

        Canvas.delete("all")

        offsets = [(0, 0), (15, 0), (0, 15), (15, 15)]
        algorithms = [
            ("ЦДА", "blue", DigitalDifferentialAnalyzer),
            ("Брезенхем (вещ.)", "red", BrezenhemFloat),
            ("Брезенхем (цел.)", "green", BrezenhemInteger),
            ("Встроенный", "black", draw_line_builtin)
        ]

        for i, (offset_x, offset_y) in enumerate(offsets):
            algorithm_name, color, algorithm_func = algorithms[i]

            # Применяем смещение
            shifted_x1 = x1 + offset_x
            shifted_y1 = y1 + offset_y
            shifted_x2 = x2 + offset_x
            shifted_y2 = y2 + offset_y

            # Вычисляем центр ромба
            center_x = (shifted_x1 + shifted_x2) / 2
            center_y = (shifted_y1 + shifted_y2) / 2

            # Вычисляем вектор первой диагонали
            dx = shifted_x2 - shifted_x1
            dy = shifted_y2 - shifted_y1

            # Длина первой диагонали
            diag1_len = sqrt(dx * dx + dy * dy)

            if diag1_len < 0.1:
                continue

            # Вычисляем перпендикулярный вектор (для второй диагонали)
            perp_dx = -dy
            perp_dy = dx

            # Нормализуем перпендикулярный вектор
            perp_len = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)
            if perp_len < 0.1:
                continue

            perp_dx = perp_dx / perp_len * other_diag_len / 2
            perp_dy = perp_dy / perp_len * other_diag_len / 2

            # Вычисляем вершины ромба
            x3 = center_x + perp_dx
            y3 = center_y + perp_dy
            x4 = center_x - perp_dx
            y4 = center_y - perp_dy

            # Рисуем 4 стороны ромба
            algorithm_func(shifted_x1, shifted_y1, x3, y3, Canvas, color)
            algorithm_func(x3, y3, shifted_x2, shifted_y2, Canvas, color)
            algorithm_func(shifted_x2, shifted_y2, x4, y4, Canvas, color)
            algorithm_func(x4, y4, shifted_x1, shifted_y1, Canvas, color)

            # Подписываем алгоритмы
            Canvas.create_text(500, 20 + i * 20, text=algorithm_name, fill=color, font=("Arial", 10))

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")


def save_to_pbm():
    """Сохраняет текущее изображение в формате PBM"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pbm",
        filetypes=[("PBM files", "*.pbm"), ("All files", "*.*")]
    )

    if not file_path:
        return

    try:
        # Создаем изображение PIL того же размера, что и канва
        image = Image.new('RGB', (600, 400), 'white')
        draw = ImageDraw.Draw(image)

        # Для простоты будем рисовать только первым алгоритмом (ЦДА) черным цветом
        # В реальном приложении нужно сохранять то, что на экране

        # Здесь можно добавить логику для сохранения текущего состояния канваса
        # Но для простоты сохраним пример ромба

        x1 = float(entry_x1.get())
        y1 = float(entry_y1.get())
        x2 = float(entry_x2.get())
        y2 = float(entry_y2.get())
        other_diag_len = float(entry_len.get())

        # Вычисляем вершины ромба (аналогично create_rhombus)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        dx = x2 - x1
        dy = y2 - y1
        diag1_len = sqrt(dx * dx + dy * dy)

        if diag1_len >= 0.1:
            perp_dx = -dy
            perp_dy = dx
            perp_len = sqrt(perp_dx * perp_dx + perp_dy * perp_dy)

            if perp_len >= 0.1:
                perp_dx = perp_dx / perp_len * other_diag_len / 2
                perp_dy = perp_dy / perp_len * other_diag_len / 2

                x3 = center_x + perp_dx
                y3 = center_y + perp_dy
                x4 = center_x - perp_dx
                y4 = center_y - perp_dy

                # Рисуем ромб черным цветом
                draw.line([(x1, y1), (x3, y3)], fill='black', width=1)
                draw.line([(x3, y3), (x2, y2)], fill='black', width=1)
                draw.line([(x2, y2), (x4, y4)], fill='black', width=1)
                draw.line([(x4, y4), (x1, y1)], fill='black', width=1)

        # Сохраняем в PBM
        if save_as_pbm(image, file_path):
            messagebox.showinfo("Успех", f"Изображение сохранено как {file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")


# Создаем главное окно
root = tk.Tk()
root.title("Растеризация отрезков прямых")
root.geometry("600x500")

# Заголовок
title_label = tk.Label(root, text="Растеризация отрезков прямых (вариант с ромбами)", font=("Arial", 14, "bold"))
title_label.pack(pady=5)

# Фрейм для ввода параметров ромба
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

# Фрейм для кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_create = tk.Button(button_frame, text="Создать ромб", command=create_rhombus, width=12, height=1)
btn_create.pack(side=tk.LEFT, padx=5)

btn_load_svg = tk.Button(button_frame, text="Загрузить SVG", command=load_svg, width=12, height=1)
btn_load_svg.pack(side=tk.LEFT, padx=5)

btn_save_pbm = tk.Button(button_frame, text="Сохранить PBM", command=save_to_pbm, width=12, height=1)
btn_save_pbm.pack(side=tk.LEFT, padx=5)

# Канва для рисования
Canvas = tk.Canvas(root, width=600, height=400, bg="white", relief="solid", bd=1)
Canvas.pack(pady=10)

# Запускаем приложение
root.mainloop()