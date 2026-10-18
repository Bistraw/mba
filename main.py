import database
from domain import Color, Source, SourceKind, SourceFrame, SourceService
import render

database.update_schema()

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
    Color(0, 0, 0),       
]

conn = database.create_connection()

s = Source()

s.sha512 = ""
s.imdb_id = ""
s.metadata_name = "TEST_SOURCE"
s.kind = SourceKind.UNKNOWN

s.id = SourceService.create_source(conn, s, False)

for i,d in enumerate(data):
    sf = SourceFrame()

    sf.source_id = s.id
    sf.color = d
    sf.frame_index = i

    sf.id = SourceService.create_source_frame(conn, s.id, sf, False)

fames = SourceService.get_source_frames(conn, s.id)

data = []

for f in fames:
    data.append(f.color)

img = render.render(data, 200, 200)

img.show()