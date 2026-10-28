import math
from PIL import Image, ImageDraw, ImageFont
from domain import Color, SourceService, SourceFrame, Source
import database
import os

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

def render_force_aspect(data : list[Color], width, height):
    img = Image.new(mode="RGB", size=(width, height))

    draw = ImageDraw.Draw(img)

    n = len(data)

    if n > width:
        colors_per_strip = int(n / width)
        strip_count = int(n / colors_per_strip)
        strip_width = 1
    else:
        colors_per_strip = 1
        strip_count = len(data)
        strip_width = int(width/strip_count)

    aux = []

    for i, d in enumerate(data):
        aux.append(d)

        if i % colors_per_strip == 0 or i == n - 1:
            color = get_color_avg(aux)
            
            aux = []

            print(f"color[{i}] = {color.as_tuple()}")
            
            draw.rectangle(
                xy=(i * strip_width, 0, i * strip_width + strip_width, height),
                fill=color.as_tuple(),
                outline=color.as_tuple(),
                width=0
            )

    return img

def render(data : list[Color], height : int = 200, strip_width : int = 1, color_per_strip : int = 1):
    n_raw = len(data)

    n = int(n_raw / color_per_strip)

    w = n * strip_width
    h = height
    
    img = Image.new(mode="RGB", size=(w, h))
    
    draw = ImageDraw.Draw(img)

    #print(f"n_raw: {n_raw}, n: {n}, w: {w}, h: {h}, s_width: {strip_width}", end="\n\n")

    x1 = 0
    y1 = 0
    x2 = strip_width
    y2 = h

    r = 0
    g = 0
    b = 0

    for i, d in enumerate(data):
        r += d.r
        g += d.g
        b += d.b

        c = d

        if i % color_per_strip == 0 or i == n_raw - 1:
            # if i != 0:
            c = Color(int(r/color_per_strip), int(g/color_per_strip), int(b/color_per_strip))
            r = 0
            g = 0
            b = 0

            #print(f"i: {i}, color: {c.as_tuple()}, x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}")
            
            draw.rectangle(
                xy=(x1, 0, x2, h - 1),
                fill=c.as_tuple()
            )

            x1 += strip_width
            y1 = 0
            x2 += strip_width
            y2 = h

    #print(f"img.width: {img.width}, img.height: {img.height}")
    
    return img

def render_force_max_lines(data : list[Color], height : int, strip_width : int, max_strips : int) -> Image:
    n = len(data)

    colors_per_strip = max(1, int(n / max_strips)) # fewer frames than strips -> one frame per strip

    return render(data, height, strip_width, colors_per_strip)

def render_force_max_lines_force_size(data : list[Color], height : int, strip_width : int, max_strips : int, width : int) -> Image:
    n = len(data)

    colors_per_strip = max(1, int(n / max_strips)) # fewer frames than strips -> one frame per strip

    img = render(data, height, strip_width, colors_per_strip)

    img = img.resize((width, height))

    return img

def test_render():
    
    data = [
        Color(255, 0, 255),   
        Color(100, 0, 255),   
        Color(0, 0, 255),     
        Color(255, 0, 0),     
        Color(255, 0, 100),   
        Color(255, 50, 150),  
        Color(255, 100, 0),   
        Color(255, 200, 0),   
        Color(255, 255, 0),   
        Color(150, 255, 0),   
        Color(0, 255, 0),     
        Color(0, 255, 100),   
        Color(0, 255, 255),   
        Color(0, 150, 255),   
        Color(100, 100, 255), 
        Color(150, 0, 255),   
        Color(255, 0, 200),   
        Color(255, 100, 100), 
        Color(255, 150, 50),  
        Color(200, 255, 0),   
        Color(0, 200, 150),   
        Color(0, 100, 200),   
        Color(100, 0, 150),   
        Color(150, 0, 100),   
        Color(255, 255, 255), 
        Color(200, 200, 200), 
        Color(128, 128, 128), 
        Color(50, 50, 50),    
        Color(255, 255, 255),       
    ]

    #img = render(data, 20, 1)
    img = render_force_max_lines(data, 20, 9)

    img.show()

def render_source(source_id : int):
    conn = database.create_connection()
    
    fames = SourceService.get_source_frames(conn, source_id)

    data = []

    for f in fames:
        data.append(f.color)

    img = render.render_force_max_lines(data, 900, 5, 1000)

    img.show()

def calc_circ_point(c_x, c_y, rad, angle):
    x = rad * math.cos(angle * (math.pi / 180)) + c_x
    y = rad * math.sin(angle * (math.pi / 180)) + c_y

    return x, y

def render_circle(data : list[Color], rad : int = 250, rad_inner: int = 20, max_strips : int = 0, width : int = 500, height : int = 500):
    img = Image.new(mode="RGBA", size=(rad * 2, rad * 2))

    draw = ImageDraw.Draw(img)

    n = len(data)

    deg_per_strip = 360 / n
    col_per_strip = 1 if max_strips == 0 or n < max_strips else int(n / max_strips)

    p1 = (rad * 2, rad)
    p2 = p1 
    p3 = (rad + rad_inner, rad)
    p4 = p3

    r = 0
    g = 0
    b = 0

    for i, d in enumerate(data):
        r += d.r
        g += d.g
        b += d.b

        if (i % col_per_strip == 0 and (i > 0 or col_per_strip == 1)) or i == n - 1:  

            if i == n - 1:
                p2 = (rad * 2, rad)
                p4 = (rad + rad_inner, rad)    
            else:
                p2 = calc_circ_point(rad, rad, rad, i * deg_per_strip)
                p4 = calc_circ_point(rad, rad, rad_inner, i * deg_per_strip)

            r = int(r / col_per_strip)
            g = int(g / col_per_strip)
            b = int(b / col_per_strip)

            # if i % col_per_strip > 0:
            #     r = int(r / i % col_per_strip)
            #     g = int(g / i % col_per_strip)
            #     b = int(b / i % col_per_strip)
            # else:

            draw.polygon(
                [p3, p1, p2,  p4],
                fill = (r, g, b)
            )

            p1 = p2
            p3 = p4

            r = 0
            g = 0
            b = 0
    
    img = img.resize((width, height))

    return img

def get_strip_colors(data : list[Color], max_strips : int) -> list[Color]:
    # averages consecutive frames so there are at most max_strips colors, in order
    n = len(data)

    strips = max(1, min(n, max_strips))

    return [get_color_avg(data[s * n // strips : (s + 1) * n // strips]) for s in range(strips)] if n else []

def get_luma(c : Color):
    # Rec. 709 brightness, same weights as the ingester
    return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b

def render_rows(data : list[Color], max_strips : int = 1000, width : int = 500, height : int = 500):
    # horizontal strips, the first frame on top
    colors = get_strip_colors(data, max_strips)

    img = Image.new(mode="RGB", size=(1, len(colors)))

    img.putdata([c.as_tuple() for c in colors])

    return img.resize((width, height), Image.NEAREST)

def render_rings(data : list[Color], rad : int = 250, rad_inner : int = 20, max_strips : int = 0, width : int = 500, height : int = 500):
    # concentric rings, the first frame in the center and the last one outside
    colors = get_strip_colors(data, max_strips or len(data))

    img = Image.new(mode="RGBA", size=(rad * 2, rad * 2))

    draw = ImageDraw.Draw(img)

    step = (rad - rad_inner) / len(colors)

    # outside in, each disc covers the center of the previous one leaving a ring
    for i in reversed(range(len(colors))):
        r = rad_inner + (i + 1) * step

        draw.ellipse((rad - r, rad - r, rad + r, rad + r), fill=colors[i].as_tuple())

    if rad_inner > 0:
        draw.ellipse((rad - rad_inner, rad - rad_inner, rad + rad_inner, rad + rad_inner), fill=(0, 0, 0, 0))

    return img.resize((width, height))

def render_spiral(data : list[Color], rad : int = 250, rad_inner : int = 20, max_strips : int = 0, width : int = 500, height : int = 500, turns : int = 6):
    # a band winding clockwise from the top, the first frame in the center
    colors = get_strip_colors(data, max_strips or len(data))
    n = len(colors)

    img = Image.new(mode="RGBA", size=(rad * 2, rad * 2))

    draw = ImageDraw.Draw(img)

    turns = max(1, turns)
    band = (rad - rad_inner) / (turns + 1)     # width of the band, the last loop ends right at rad
    total = turns * 360                         # degrees covered by the whole movie
    steps = max(1, math.ceil(total / n / 3))    # an edge point every ~3 degrees so long strips stay curved

    def edge(angle, outer):
        # the inner edge of the band grows one band width per turn
        r = rad_inner + band * angle / 360 + (band if outer else 0)

        return calc_circ_point(rad, rad, r, angle - 90)

    for i, c in enumerate(colors):
        a0 = total * i / n
        a1 = total * (i + 1) / n

        angles = [a0 + (a1 - a0) * k / steps for k in range(steps + 1)]

        polygon = [edge(a, True) for a in angles] + [edge(a, False) for a in reversed(angles)]

        draw.polygon(polygon, fill=c.as_tuple())

    return img.resize((width, height))

def render_mosaic(data : list[Color], max_strips : int = 1000, width : int = 500, height : int = 500):
    # one tile per strip, read left to right and top to bottom, as square as the size allows
    colors = get_strip_colors(data, max_strips)
    n = len(colors)

    cols = max(1, round(math.sqrt(n * width / height)))
    rows = math.ceil(n / cols)

    tile_w = width / cols
    tile_h = height / rows
    gap = int(min(tile_w, tile_h) * 0.1)   # thin dark gap between tiles, none when they are tiny

    img = Image.new(mode="RGBA", size=(width, height))

    draw = ImageDraw.Draw(img)

    for i, c in enumerate(colors):
        x = (i % cols) * tile_w
        y = (i // cols) * tile_h

        draw.rectangle((int(x), int(y), int(x + tile_w) - 1 - gap, int(y + tile_h) - 1 - gap), fill=c.as_tuple())

    return img

def render_wave(data : list[Color], max_strips : int = 1000, width : int = 500, height : int = 500):
    # vertical bars centered on the middle, as tall as the strip is bright (the brightest one fills the height)
    colors = get_strip_colors(data, max_strips)
    n = len(colors)

    lumas = [get_luma(c) for c in colors]
    top = max(lumas) or 1

    img = Image.new(mode="RGBA", size=(width, height))

    draw = ImageDraw.Draw(img)

    for i, (c, y) in enumerate(zip(colors, lumas)):
        x0 = int(i * width / n)
        x1 = max(x0, int((i + 1) * width / n) - 1)

        h = height * (0.06 + 0.94 * y / top)   # dark moments keep a sliver so the bar stays visible

        draw.rectangle((x0, int((height - h) / 2), x1, int((height + h) / 2)), fill=c.as_tuple())

    return img

def test_render_circle():
    
    data = [
        Color(255, 0, 255),   
        Color(100, 0, 255),   
        Color(0, 0, 255),     
        Color(255, 0, 0),     
        Color(255, 0, 100),   
        Color(255, 50, 150),  
        Color(255, 100, 0),   
        Color(255, 200, 0),   
        Color(255, 255, 0),   
        Color(150, 255, 0),   
        Color(0, 255, 0),     
        Color(0, 255, 100),   
        Color(0, 255, 255),   
        Color(0, 150, 255),   
        Color(100, 100, 255), 
        Color(150, 0, 255),   
        Color(255, 0, 200),   
        Color(255, 100, 100), 
        Color(255, 150, 50),  
        Color(200, 255, 0),   
        Color(0, 200, 150),   
        Color(0, 100, 200),   
        Color(100, 0, 150),   
        Color(150, 0, 100),   
        Color(255, 255, 255), 
        Color(200, 200, 200), 
        Color(128, 128, 128), 
        Color(50, 50, 50),    
        Color(255, 255, 255),      
        Color(255, 0, 255),   
        Color(100, 0, 255),   
        Color(0, 0, 255),     
        Color(255, 0, 0),     
        Color(255, 0, 100),   
        Color(255, 50, 150),  
        Color(255, 100, 0),   
        Color(255, 200, 0),   
        Color(255, 255, 0),   
        Color(150, 255, 0),   
        Color(0, 255, 0),     
        Color(0, 255, 100),   
        Color(0, 255, 255),   
        Color(0, 150, 255),   
        Color(100, 100, 255), 
        Color(150, 0, 255),   
        Color(255, 0, 200),   
        Color(255, 100, 100), 
        Color(255, 150, 50),  
        Color(200, 255, 0),   
        Color(0, 200, 150),   
        Color(0, 100, 200),   
        Color(100, 0, 150),   
        Color(150, 0, 100),   
        Color(255, 255, 255), 
        Color(200, 200, 200), 
        Color(128, 128, 128), 
        Color(50, 50, 50),    
        Color(255, 255, 255),  
        Color(255, 0, 255),   
        Color(100, 0, 255),   
        Color(0, 0, 255),     
        Color(255, 0, 0),     
        Color(255, 0, 100),   
        Color(255, 50, 150),  
        Color(255, 100, 0),   
        Color(255, 200, 0),   
        Color(255, 255, 0),   
        Color(150, 255, 0),   
        Color(0, 255, 0),     
        Color(0, 255, 100),   
        Color(0, 255, 255),   
        Color(0, 150, 255),   
        Color(100, 100, 255), 
        Color(150, 0, 255),   
        Color(255, 0, 200),   
        Color(255, 100, 100), 
        Color(255, 150, 50),  
        Color(200, 255, 0),   
        Color(0, 200, 150),   
        Color(0, 100, 200),   
        Color(100, 0, 150),   
        Color(150, 0, 100),   
        Color(255, 255, 255), 
        Color(200, 200, 200), 
        Color(128, 128, 128), 
        Color(50, 50, 50),    
        Color(255, 255, 255),      
        Color(255, 0, 255),   
        Color(100, 0, 255),   
        Color(0, 0, 255),     
        Color(255, 0, 0),     
        Color(255, 0, 100),   
        Color(255, 50, 150),  
        Color(255, 100, 0),   
        Color(255, 200, 0),   
        Color(255, 255, 0),   
        Color(150, 255, 0),   
        Color(0, 255, 0),     
        Color(0, 255, 100),   
        Color(0, 255, 255),   
        Color(0, 150, 255),   
        Color(100, 100, 255), 
        Color(150, 0, 255),   
        Color(255, 0, 200),   
        Color(255, 100, 100), 
        Color(255, 150, 50),  
        Color(200, 255, 0),   
        Color(0, 200, 150),   
        Color(0, 100, 200),   
        Color(100, 0, 150),   
        Color(150, 0, 100),   
        Color(255, 255, 255), 
        Color(200, 200, 200), 
        Color(128, 128, 128), 
        Color(50, 50, 50),    
        Color(255, 255, 255),  
    ]

    print(f"data lenght: {len(data)}")

    img = render_circle(data, 1000, 200, 24, 1000, 1000)

    img.show()

def render_frame(text_left : str, text_right : str, framed_img : Image, background_color : Color, foreground_color : Color, header_height : int, width : int, height : int):
    img = Image.new(mode="RGBA", size=(width, height), color = background_color.as_tuple())

    padding = 20

    c_img_w = width - (2 * padding)
    c_img_h = height - (2 * padding) - header_height
    c_img = framed_img.resize((c_img_w, c_img_h))

    off_w = padding
    off_h = padding + header_height

    # shapes with transparent areas (circle, rings...) let the frame background show through
    img.paste(c_img, (off_w, off_h), c_img if c_img.mode == "RGBA" else None)

    draw = ImageDraw.Draw(img)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    font_path = os.path.join(dir_path, "assets", "fonts", "sans_serif", "SansSerifBookFLF.otf")

    font = ImageFont.truetype(font_path, 16, )

    draw.text((padding, padding), text_left, foreground_color.as_tuple(), font=font, anchor="ls")
    draw.text((width - padding, padding), text_right, foreground_color.as_tuple(), font=font, anchor="rs")

    return img

if __name__ == "__main__":  
    #test_render()
    database.update_schema()
    
    #render_source(15)

    test_render_circle()