import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def compute_code(x, y, x_min, y_min, x_max, y_max):
    code = INSIDE
    if x < x_min:
        code |= LEFT
    elif x > x_max:
        code |= RIGHT
    if y < y_min:
        code |= BOTTOM
    elif y > y_max:
        code |= TOP
    return code


def cohen_sutherland_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
    code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)
    accept = False

    while True:
        if code1 == 0 and code2 == 0:
            accept = True
            break
        elif (code1 & code2) != 0:
            break
        else:
            code_out = code1 if code1 != 0 else code2

            if code_out & TOP:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code_out & BOTTOM:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code_out & RIGHT:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code_out & LEFT:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min

            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)

    if accept:
        return [(x1, y1), (x2, y2)]
    else:
        return None


def main():
    print("Алгоритм отсечения Сазерленда-Коэна")
    print("=====================================")

    x_min = float(input("Введите x левой границы окна: "))
    y_min = float(input("Введите y нижней границы окна: "))
    x_max = float(input("Введите x правой границы окна: "))
    y_max = float(input("Введите y верхней границы окна: "))

    n = int(input("Введите количество отрезков: "))

    segments = []
    for i in range(n):
        print(f"\nОтрезок {i + 1}:")
        x1 = float(input("x1: "))
        y1 = float(input("y1: "))
        x2 = float(input("x2: "))
        y2 = float(input("y2: "))
        segments.append(((x1, y1), (x2, y2)))

    clipped_segments = []
    for segment in segments:
        (x1, y1), (x2, y2) = segment
        clipped = cohen_sutherland_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max)
        if clipped:
            clipped_segments.append(clipped)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    rect1 = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                     linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax1.add_patch(rect1)

    for segment in segments:
        (x1, y1), (x2, y2) = segment
        ax1.plot([x1, x2], [y1, y2], 'red', linewidth=2)

    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('Исходные отрезки')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    rect2 = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                     linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect2)

    for segment in clipped_segments:
        (x1, y1), (x2, y2) = segment
        ax2.plot([x1, x2], [y1, y2], 'blue', linewidth=3)

    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title('Отсеченные отрезки')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')

    plt.tight_layout()
    plt.show()

    print("\nРезультаты отсечения:")
    print("====================")
    for i, segment in enumerate(clipped_segments):
        (x1, y1), (x2, y2) = segment
        print(f"Отсеченный отрезок {i + 1}: ({x1:.2f}, {y1:.2f}) - ({x2:.2f}, {y2:.2f})")


if __name__ == "__main__":
    main()