from PIL import Image, ImageDraw
from domain import Color

def render(data : list[Color], width, height):
    img = Image.new(mode="RGB", size=(width, height))

    draw = ImageDraw.Draw(img)

    strip_count = len(data)
    strip_width = width/strip_count

    for i, color in enumerate(data):
        print(f"color[{i}] = {color.as_tuple()}")
        
        draw.rectangle(
            xy=(i * strip_width, 0, i * strip_width + strip_width, height),
            fill=color.as_tuple(),
            outline=color.as_tuple(),
            width=0
        )

    return img

def test_render():
    data = [
        Color(255, 0, 255),
        Color(100, 0, 255),
        Color(0, 0, 255),
        Color(255, 0, 0),
    ]

    img = render(data, 200, 200)

    img.show()

if __name__ == "__main__":  
    test_render()