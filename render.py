from PIL import Image, ImageDraw
from domain import Color, SourceService, SourceFrame, Source
import database

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

    print(f"n_raw: {n_raw}, n: {n}, w: {w}, h: {h}, s_width: {strip_width}", end="\n\n")

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

            print(f"i: {i}, color: {c.as_tuple()}, x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}")
            
            draw.rectangle(
                xy=(x1, 0, x2, h - 1),
                fill=c.as_tuple()
            )

            x1 += strip_width
            y1 = 0
            x2 += strip_width
            y2 = h

    print(f"img.width: {img.width}, img.height: {img.height}")
    
    return img

def render_force_max_lines(data : list[Color], height : int, strip_width : int, max_strips : int) -> Image:
    n = len(data)

    colors_per_strip = int(n / max_strips)

    return render(data, height, strip_width, colors_per_strip)

def render_force_max_lines_force_size(data : list[Color], height : int, strip_width : int, max_strips : int, width : int) -> Image:
    n = len(data)

    colors_per_strip = int(n / max_strips)

    img = render(data, height, strip_width, colors_per_strip)

    if img.width > width:
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

if __name__ == "__main__":  
    #test_render()
    database.update_schema()
    
    render_source(15)