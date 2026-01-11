import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math

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


def midpoint_clip_segment(x1, y1, x2, y2, x_min, y_min, x_max, y_max, epsilon=1e-6):

    code1 = compute_code(x1, y1, x_min, y_min, x_max, y_max)
    code2 = compute_code(x2, y2, x_min, y_min, x_max, y_max)

    if code1 == 0 and code2 == 0:
        return [(x1, y1), (x2, y2)]

    if (code1 & code2) != 0:
        return None

    if math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) < epsilon:

        xm = (x1 + x2) / 2
        ym = (y1 + y2) / 2
        if compute_code(xm, ym, x_min, y_min, x_max, y_max) == 0:
            return [(xm, ym), (xm, ym)]
        else:
            return None

    xm = (x1 + x2) / 2
    ym = (y1 + y2) / 2

    left_segment = midpoint_clip_segment(x1, y1, xm, ym, x_min, y_min, x_max, y_max, epsilon)
    right_segment = midpoint_clip_segment(xm, ym, x2, y2, x_min, y_min, x_max, y_max, epsilon)

    if left_segment and right_segment:
        return [(left_segment[0][0], left_segment[0][1]),
                (right_segment[1][0], right_segment[1][1])]
    elif left_segment:
        return left_segment
    elif right_segment:
        return right_segment
    else:
        return None


def midpoint_clip(segments, x_min, y_min, x_max, y_max, epsilon=1e-6):
    clipped_segments = []

    for segment in segments:
        (x1, y1), (x2, y2) = segment
        clipped = midpoint_clip_segment(x1, y1, x2, y2, x_min, y_min, x_max, y_max, epsilon)
        if clipped:
            clipped_segments.append(clipped)

    return clipped_segments


def main():
    print("Программа для отсечения отрезков")
    print("=====================================")
    print("Реализованы алгоритмы:")
    print("1. Алгоритм Сазерленда-Коэна")
    print("2. Алгоритм разбиения средней точкой")

    print("\nВведите параметры окна отсечения:")
    x_min = float(input("x левой границы окна: "))
    y_min = float(input("y нижней границы окна: "))
    x_max = float(input("x правой границы окна: "))
    y_max = float(input("y верхней границы окна: "))

    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min

    n = int(input("\nВведите количество отрезков: "))

    segments = []
    for i in range(n):
        print(f"\nОтрезок {i + 1}:")
        x1 = float(input("x1: "))
        y1 = float(input("y1: "))
        x2 = float(input("x2: "))
        y2 = float(input("y2: "))
        segments.append(((x1, y1), (x2, y2)))

    cs_clipped_segments = []
    for segment in segments:
        (x1, y1), (x2, y2) = segment
        clipped = cohen_sutherland_clip(x1, y1, x2, y2, x_min, y_min, x_max, y_max)
        if clipped:
            cs_clipped_segments.append(clipped)

    mp_clipped_segments = midpoint_clip(segments, x_min, y_min, x_max, y_max)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    ax1 = axes[0]
    rect1 = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                      linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax1.add_patch(rect1)

    for segment in segments:
        (x1, y1), (x2, y2) = segment
        ax1.plot([x1, x2], [y1, y2], 'red', linewidth=2, marker='o', markersize=4)

    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('Исходные отрезки')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    ax2 = axes[1]
    rect2 = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                      linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect2)

    for segment in cs_clipped_segments:
        (x1, y1), (x2, y2) = segment
        ax2.plot([x1, x2], [y1, y2], 'blue', linewidth=3, marker='s', markersize=5)

    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_title('Алгоритм Сазерленда-Коэна')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')

    ax3 = axes[2]
    rect3 = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                      linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax3.add_patch(rect3)

    for segment in mp_clipped_segments:
        (x1, y1), (x2, y2) = segment
        ax3.plot([x1, x2], [y1, y2], 'green', linewidth=3, marker='^', markersize=5)

    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_title('Алгоритм разбиения средней точкой')
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal')

    plt.tight_layout()
    plt.show()

    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ ОТСЕЧЕНИЯ:")
    print("=" * 50)

    print("\n1. Алгоритм Сазерленда-Коэна:")
    if cs_clipped_segments:
        for i, segment in enumerate(cs_clipped_segments):
            (x1, y1), (x2, y2) = segment
            print(f"   Отрезок {i + 1}: ({x1:.4f}, {y1:.4f}) - ({x2:.4f}, {y2:.4f})")
    else:
        print("   Нет видимых отрезков")

    print("\n2. Алгоритм разбиения средней точкой:")
    if mp_clipped_segments:
        for i, segment in enumerate(mp_clipped_segments):
            (x1, y1), (x2, y2) = segment
            print(f"   Отрезок {i + 1}: ({x1:.4f}, {y1:.4f}) - ({x2:.4f}, {y2:.4f})")
    else:
        print("   Нет видимых отрезков")

    print("\n" + "=" * 50)
    print("СРАВНЕНИЕ АЛГОРИТМОВ:")
    print("=" * 50)
    print(f"Количество отрезков после отсечения:")
    print(f"  Сазерленд-Коэн: {len(cs_clipped_segments)}")
    print(f"  Разбиение средней точкой: {len(mp_clipped_segments)}")

    if len(cs_clipped_segments) == len(mp_clipped_segments):
        print("\n✓ Оба алгоритма дали одинаковое количество видимых отрезков")
    else:
        print("\n⚠ Алгоритмы дали разное количество видимых отрезков")
        print("  (возможно, из-за разной точности вычислений)")


if __name__ == "__main__":
    main()