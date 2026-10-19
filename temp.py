import math
from PIL import Image, ImageDraw
from domain import Color, SourceService, SourceFrame, Source

def calc_circ_point(c_x, c_y, rad, angle):
    x = rad * math.cos(angle * (math.pi / 180)) + c_x
    y = rad * math.sin(angle * (math.pi / 180)) + c_y

    return x, y

def render_circle(data : list[Color], rad : int = 250, rad_inner: int = 20, max_strips : int = 0, width : int = 500, height : int = 500):
    img = Image.new(mode="RGB", size=(rad * 2, rad * 2))

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

if __name__ == "__main__":
    
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

    #x, y = calc_circ_point(5, 5, 5, 90)

    #print(f"x: {x}, y: {y}")