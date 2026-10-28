import requests
import database
import environment
from domain import *
import os
import hash
import ingester

def create_source_from_file(file_path : str) -> Source:
    conn = database.create_connection()

    s = Source()

    s.sha512 = "s3"
    s.imdb_id = "3"
    s.metadata_name = "TEST_SOURCE"
    s.kind = SourceKind.UNKNOWN

    s.id = SourceService.create_source(conn, s, False)

    ingest_source_frames(conn, s.id, file_path)

    conn.commit()

    return s

def ingest_source_frames(conn, source_id : int, file_path : str):
    # stores every color mode of every frame, the caller commits
    colors = ingester.ingest_colors(file_path)

    frames = []

    for idx, (avg, bright) in enumerate(zip(ingester.to_colors(colors[ColorMode.AVERAGE]), ingester.to_colors(colors[ColorMode.BRIGHTEST]))):
        sf = SourceFrame()

        sf.source_id = source_id
        sf.color = avg
        sf.bright_color = bright
        sf.frame_index = idx

        frames.append(sf)

    SourceService.create_source_frames(conn, source_id, frames, False)

    for mode in ColorMode.BLOB_MODES:
        SourceService.set_source_colors(conn, source_id, mode, colors[mode].tobytes(), False)

def backfill_source_colors(conn, source_id : int, file_path : str, missing_modes : list[int]):
    # sources ingested before a color mode existed don't have it, fill those in
    print(f"backfilling color modes {missing_modes} for source id: {source_id}, path: {file_path}")

    colors = ingester.ingest_colors(file_path)

    frame_count = SourceService.get_source_frame_count(conn, source_id)
    file_count = len(colors[ColorMode.AVERAGE])

    if file_count != frame_count:
        print(f"frame count mismatch (db: {frame_count}, file: {file_count}), the file may be a different release. Skipping.")
        return

    for mode in missing_modes:
        if mode == ColorMode.BRIGHTEST:
            SourceService.update_source_frames_bright(conn, source_id, ingester.to_colors(colors[mode]), False)
        else:
            SourceService.set_source_colors(conn, source_id, mode, colors[mode].tobytes(), False)

    conn.commit()

    print(f"color modes stored for source id: {source_id}")

def feed_jellyfin_items():
    url = f"http://localhost:8096/items?apikey={environment.JELLY_APIKEY}&recursive=true&hasImdbId=true&includeItemTypes=Movie&fields=ProviderIds,Path"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching items from Jellyfin: {response.status_code} - {response.text}")
        return

    response_json = response.json()

    print(f"fetched {len(response_json['Items'])} items from Jellyfin.")

    conn = database.create_connection()
    
    for i in response_json["Items"]:

        try:
            s = Source()

            if not i["Type"] == "Movie":
                print(f"Item is not a movie. Type: {i['Type']}")
                continue
            
            if not "ProviderIds" in i.keys():
                print(f"Item does not have ProviderIds. Skipping.")
                continue

            if not "Imdb" in i["ProviderIds"].keys():
                print(f"Item does not have Imdb id. Skipping.")
                continue

            if not "Path" in i.keys():
                print(f"Item does not have Path. Skipping.")
                continue

            if not "Name" in i.keys():
                print(f"Item does not have Name. Skipping.")
                continue

            if not "ProductionYear" in i.keys():
                print(f"Item does not have ProductionYear. Skipping.")
                continue

            s.imdb_id = i["ProviderIds"]["Imdb"]
            s.path = i["Path"]
            s.kind = SourceKind.MOVIE
            s.metadata_name = i["Name"]
            s.metadata_year = int(i["ProductionYear"])

            print(f"processing file, path: {s.path}")

            if not os.path.exists(s.path):
                print(f"File does not exist: {s.path}")
                continue

            existing_id = SourceService.get_source_id_by_imdb_id(conn, s.imdb_id)

            if existing_id is not None:
                missing_modes = SourceService.get_missing_color_modes(conn, existing_id)

                if missing_modes:
                    backfill_source_colors(conn, existing_id, s.path, missing_modes)
                else:
                    print(f"source already exists, imdb_id matched: {s.imdb_id}")

                continue
            
            s.sha512 = hash.get_audio_hash_sha512(s.path)

            if SourceService.do_source_exists(conn, s.sha512, ""):   
                print(f"source already exists, hash matched: {s.sha512}")
                continue

            s.id = SourceService.create_source(conn, s, False)

            print(f"source created. imdb_id: {s.imdb_id}, path: {s.path}, id: {s.id}, name: {s.metadata_name}, year: {s.metadata_year}, sha512: {s.sha512}")
            print(f"ingesting source frames for source id: {s.id}")

            ingest_source_frames(conn, s.id, s.path)

            conn.commit()

        except Exception as e:
            conn.rollback()

            print(f"error processing item, exception: {repr(e)}")

if __name__ == "__main__":
    #file_path = r"D:\Videos\Movies\[MTBB] Mushoku Tensei (BD 1080p)\[MTBB] Mushoku Tensei - 01v3 [0C3C916A].mkv"
    #file_path = r"D:\Videos\Movies\Black Swan (2010) [1080p] [BluRay] [5.1] [YTS.MX]\Black.Swan.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"
    #file_path = r"D:\Videos\Movies\Eternal Sunshine of the Spotless Mind (2004) [1080p]\Eternal.Sunshine.of.the.Spotless.Mind.2004.1080p.BrRip.x264.BOKUTOX.YIFY.mp4"
    #file_path = r"D:\Videos\Movies\Arco (2025) [HYBRID] [1080p] [BluRay] [5.1] [YTS.BZ]\Arco.2025.HYBRID.1080p.BluRay.x264.AAC5.1-[YTS.BZ].mp4"            
    #s = create_source_from_file(file_path)
    #print(f"source_id: {s.id}")
    #render_source(s.id)

    feed_jellyfin_items()