import database
from domain import Color, Source, SourceKind, SourceFrame, SourceService
import render
import ingester

database.update_schema()

def create_source_from_file(file_path : str) -> Source:
    conn = database.create_connection()

    s = Source()

    s.sha512 = "s3"
    s.imdb_id = "3"
    s.metadata_name = "TEST_SOURCE"
    s.kind = SourceKind.UNKNOWN

    s.id = SourceService.create_source(conn, s, False)

    data = ingester.ingest(file_path)

    for i,d in enumerate(data):
        sf = SourceFrame()

        sf.source_id = s.id
        sf.color = d
        sf.frame_index = i

        sf.id = SourceService.create_source_frame(conn, s.id, sf, False)

    conn.commit()

    return s

def render_source(source_id : int):
    conn = database.create_connection()
    
    fames = SourceService.get_source_frames(conn, source_id)

    data = []

    for f in fames:
        data.append(f.color)

    img = render.render_force_max_lines(data, 900, 5, 1000)

    img.show()

if __name__ == "__main__":
    #file_path = r"D:\Videos\Movies\[MTBB] Mushoku Tensei (BD 1080p)\[MTBB] Mushoku Tensei - 01v3 [0C3C916A].mkv"
    #file_path = r"D:\Videos\Movies\Black Swan (2010) [1080p] [BluRay] [5.1] [YTS.MX]\Black.Swan.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"
    #file_path = r"D:\Videos\Movies\Eternal Sunshine of the Spotless Mind (2004) [1080p]\Eternal.Sunshine.of.the.Spotless.Mind.2004.1080p.BrRip.x264.BOKUTOX.YIFY.mp4"
    #file_path = r"D:\Videos\Movies\Arco (2025) [HYBRID] [1080p] [BluRay] [5.1] [YTS.BZ]\Arco.2025.HYBRID.1080p.BluRay.x264.AAC5.1-[YTS.BZ].mp4"
            
    #s = create_source_from_file(file_path)
    
    #print(f"source_id: {s.id}")

    #render_source(s.id)

    render_source(9)