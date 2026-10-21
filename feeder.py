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

    data = ingester.ingest(file_path)

    for i,d in enumerate(data):
        sf = SourceFrame()

        sf.source_id = s.id
        sf.color = d
        sf.frame_index = i

        sf.id = SourceService.create_source_frame(conn, s.id, sf, False)

    conn.commit()

    return s

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

            if SourceService.do_source_exists(conn, "", s.imdb_id):   
                print(f"source already exists, imdb_id matched: {s.imdb_id}")
                continue
            
            s.sha512 = hash.get_audio_hash_sha512(s.path)

            if SourceService.do_source_exists(conn, s.sha512, ""):   
                print(f"source already exists, hash matched: {s.sha512}")
                continue

            s.id = SourceService.create_source(conn, s, False)

            print(f"source created. imdb_id: {s.imdb_id}, path: {s.path}, id: {s.id}, name: {s.metadata_name}, year: {s.metadata_year}, sha512: {s.sha512}")
            print(f"ingesting source frames for source id: {s.id}")

            data = ingester.ingest(s.path)

            for i,d in enumerate(data):
                sf = SourceFrame()

                sf.source_id = s.id
                sf.color = d
                sf.frame_index = i

                sf.id = SourceService.create_source_frame(conn, s.id, sf, False)
            
            conn.commit()

        except Exception as e:
            conn.rollback()

            print(f"error processing item, exception: {repr(e)}")

def get_jellyfin_items():
    pass

def feed_item_to_remote_api(s : Source, f : list[SourceFrame]):
    pass

def feed_item_to_local_db(s : Source, f : list[SourceFrame]):
    pass

def feed(input : str = "jellyfin", destiny : str = "remote"):
    
    items = []

    if input == "jellyfin":
        items = get_jellyfin_items()
    
    if destiny == "remote":
        for i in items:

            content = {
                "imdb_id": i["imdb_id"]
                ""
            }




    pass

if __name__ == "__main__":
    #file_path = r"D:\Videos\Movies\[MTBB] Mushoku Tensei (BD 1080p)\[MTBB] Mushoku Tensei - 01v3 [0C3C916A].mkv"
    #file_path = r"D:\Videos\Movies\Black Swan (2010) [1080p] [BluRay] [5.1] [YTS.MX]\Black.Swan.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"
    #file_path = r"D:\Videos\Movies\Eternal Sunshine of the Spotless Mind (2004) [1080p]\Eternal.Sunshine.of.the.Spotless.Mind.2004.1080p.BrRip.x264.BOKUTOX.YIFY.mp4"
    #file_path = r"D:\Videos\Movies\Arco (2025) [HYBRID] [1080p] [BluRay] [5.1] [YTS.BZ]\Arco.2025.HYBRID.1080p.BluRay.x264.AAC5.1-[YTS.BZ].mp4"            
    #s = create_source_from_file(file_path)
    #print(f"source_id: {s.id}")
    #render_source(s.id)

    feed_jellyfin_items()