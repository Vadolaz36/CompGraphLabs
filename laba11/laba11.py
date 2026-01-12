import numpy as np
import matplotlib.pyplot as plt


def tetra():
    v = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float)
    e = [(i, j) for i in range(4) for j in range(i + 1, 4)]
    f = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    return v, e, f


def octa():
    v = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    e = []
    for i in range(6):
        for j in range(i + 1, 6):
            if np.allclose(v[i], -v[j]): continue
            e.append((i, j))
    f = [
        (0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2),
        (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)
    ]
    return v, e, f


def Rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def normalize(v):
    return v / np.max(np.linalg.norm(v, axis=1))


def save_to_obj(filename, vertices, faces, name=None):
    with open(filename, 'w') as f:
        f.write(f"# Экспорт из программы визуализации многогранников\n")
        f.write(f"# Количество вершин: {len(vertices)}, граней: {len(faces)}\n\n")

        if name:
            f.write(f"o {name}\n")

        for i, vertex in enumerate(vertices):
            x, y, z = vertex
            f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")

        f.write("\n")

        for face in faces:
            face_indices = [str(idx + 1) for idx in face]
            f.write(f"f {' '.join(face_indices)}\n")

        print(f"Файл '{filename}' успешно сохранен!")
        print(f"  Вершин: {len(vertices)}")
        print(f"  Граней: {len(faces)}")


def draw(v, e, title, R):
    v = normalize(v)
    p = (R @ v.T).T
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    for i, j in e:
        z = (p[i, 2] + p[j, 2]) / 2
        style = 'k-' if z > 0 else 'k--'
        lw = 1.8 if z > 0 else 1.2
        ax.plot([p[i, 0], p[j, 0]], [p[i, 1], p[j, 1]], style, linewidth=lw)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title)


def main():
    R = Rz(np.deg2rad(30)) @ Ry(np.deg2rad(20)) @ Rx(np.deg2rad(10))

    print("ТЕТРАЭДР")
    v, e, f = tetra()
    draw(v, e, 'Тетраэдр', R)
    save_to_obj("Тетраэдр.obj", v, f, "Тетраэдр")

    print("\nОКТАЭДР ")
    v, e, f = octa()
    draw(v, e, 'Октаэдр', R)
    save_to_obj("Октаэдр.obj", v, f, "Октаэдр")

    plt.show()

if __name__ == "__main__":
    main()