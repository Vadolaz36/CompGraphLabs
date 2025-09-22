from PIL import Image


def main():
    try:
        image = Image.open('orig.jpg').convert('RGB')
    except FileNotFoundError:
        print("Ошибка: Файл orig.jpg не найден!")
        print("Положите ваше фото в ту же папку что и программу")
        return

    width, height = image.size
    pixels = image.load()

    pixels[0, 0] = (255, 127, 127)
    pixels[width // 2, 0] = (127, 255, 127)
    pixels[0, height - 1] = (127, 127, 255)


    image.save('origV2.png')
    print("Изображение сохранено как origV2.png")

    save_as_pbm('orig.jpg', 'origV2.pbm')


def save_as_pbm(input_path, output_path):
    """Сохраняет изображение в текстовом PBM формате"""
    image = Image.open(input_path).convert('1')
    width, height = image.size

    with open(output_path, 'w') as file:
        file.write(f"P1\n{width} {height}\n")

        for y in range(height):
            row = []
            for x in range(width):
                pixel_value = 1 if image.getpixel((x, y)) > 0 else 0
                row.append(str(pixel_value))
            file.write(' '.join(row) + '\n')

    print("PBM файл сохранён как origV2.pbm")

if __name__ == "__main__":
    main()