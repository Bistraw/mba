import math
from PIL import Image
from domain import Color

def clamp(min_value, max_value, value):
    if value < min_value:
        value = min_value

    if value > max_value:
        value = max_value

    return value

def get_color_avg(data : list[Color]):
    n = len(data)
    
    r = 0
    g = 0
    b = 0
    
    for d in data:
        r += d.r
        g += d.g
        b += d.b

    return Color(int(r/n), int(g/n), int(b/n))

# get a point in the circle circunference

def calc_circ_point(c_x, c_y, rad, angle):
    x = rad * math.cos(angle * (math.pi / 180)) + c_x
    y = rad * math.sin(angle * (math.pi / 180)) + c_y

    return x, y

# replace all pixels with alpha value 0 with the color provided

def paint_transparent_pixels(img : Image, replace_color : Color):
    new_data = []

    data = img.getdata()

    for d in data:
        # print("d: ", d)

        if len(d) > 3 and d[3] == 0:
            new_data.append(replace_color.as_tuple())
        else:
            new_data.append(d)

    img.putdata(new_data)

    return img
