import requests
import database
import environment
from domain import *
import os
import hash
import ingester

def create_source_from_file(file_path : str, imdb_id : str, sha512 : str, metadata_name : str, metadata_year : int, kind : int) -> Source:
    conn = database.create_connection()

    s = Source()

    s.sha512 = sha512
    s.imdb_id = imdb_id
    s.metadata_name = metadata_name
    s.kind = kind

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

def feed_jellyfin_items(destiny : str = "remote"):
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

            s = Source()

            s.imdb_id = i["ProviderIds"]["Imdb"]
            s.kind = SourceKind.MOVIE
            s.metadata_name = i["Name"]
            s.metadata_year = int(i["ProductionYear"])

            #print(f"processing file, path: {s.path}")

            # if we already have a source created for that movie id we skip it

            if destiny == "remote":
                response = requests.get(f"{environment.REMOTE_ADDRESS}/api/source/lookup?imdb_id={s.imdb_id}")

                if response.status_code != 404:
                    print(f"source already exists for imdb_id: {s.imdb_id}")
                    continue
            else:
                if SourceService.do_source_exists(conn, "", s.imdb_id):   
                    print(f"source already exists for imdb_id: {s.imdb_id}")
                    continue
                                    
            file_path = i["Path"] 

            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                continue

            s.sha512 = hash.get_audio_hash_sha512(file_path)
            
            # if we already have a source created for that one file we can skip it

            if destiny == "remote":
                response = requests.get(f"{environment.REMOTE_ADDRESS}/api/source/lookup?sha512={s.sha512}")
                
                if response.status_code != 404:
                    print(f"source already exists for sha512: {s.sha512}")
                    continue
            else:
                if SourceService.do_source_exists(conn, s.sha512, ""):   
                    print(f"source already exists for sha512: {s.sha512}")
                    continue

            # so all is good, now we create the source

            if destiny == "remote":
                pass
            else:
                s.id = SourceService.create_source(conn, s, False)
                
                print(f"source created. id: {s.id}, imdb_id: {s.imdb_id}, path: {file_path}, id: {s.id}, name: {s.metadata_name}, year: {s.metadata_year}, sha512: {s.sha512}. ingesting frames...")

            frames = ingester.ingest(file_path)
            r_frames = []

            for i, f in enumerate(frames):
                sf = SourceFrame()

                sf.source_id = s.id
                sf.color = f
                sf.frame_index = i

                if destiny == "remote":
                    rf = {
                        "color_r" : f.r,
                        "color_g" : f.g,
                        "color_b" : f.b
                    }

                    r_frames.append(rf)
                else:
                    sf.id = SourceService.create_source_frame(conn, s.id, sf, False)

            if destiny == "remote":
                response = requests.post(
                f"{environment.REMOTE_ADDRESS}/api/source?key={environment.REMOTE_APIKEY}", 
                headers={"content-type": "application/json"}, 
                json={
                    "sha512": s.sha512, 
                    "imdb_id": s.imdb_id, 
                    "kind": s.kind, 
                    "metadata_name": s.metadata_name, 
                    "metadata_year": s.metadata_year, 
                    "frames": r_frames
                })

                if response.status_code != 200:
                    print(f"remote request failed with status_code: {response.status_code}")
                    continue

                response_json = response.json() 

                s.id = response_json["source_id"]

                frame_count = response_json["frame_count"]

                print(f"source created on remote. id: {s.id}, imdb_id: {s.imdb_id}, item: {s.metadata_name} ({s.metadata_year}), frame_count: {frame_count}")
                
            else:
                conn.commit()

        except Exception as e:
            conn.rollback()

            print(f"exception raise while processing item: {repr(e)}")

if __name__ == "__main__":
    #file_path = r"D:\Videos\Movies\[MTBB] Mushoku Tensei (BD 1080p)\[MTBB] Mushoku Tensei - 01v3 [0C3C916A].mkv"
    #file_path = r"D:\Videos\Movies\Black Swan (2010) [1080p] [BluRay] [5.1] [YTS.MX]\Black.Swan.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"
    #file_path = r"D:\Videos\Movies\Eternal Sunshine of the Spotless Mind (2004) [1080p]\Eternal.Sunshine.of.the.Spotless.Mind.2004.1080p.BrRip.x264.BOKUTOX.YIFY.mp4"
    #file_path = r"D:\Videos\Movies\Arco (2025) [HYBRID] [1080p] [BluRay] [5.1] [YTS.BZ]\Arco.2025.HYBRID.1080p.BluRay.x264.AAC5.1-[YTS.BZ].mp4"            
    #s = create_source_from_file(file_path)
    #print(f"source_id: {s.id}")
    #render_source(s.id)

    feed_jellyfin_items(destiny="remote")