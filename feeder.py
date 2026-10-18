import requests
import database
import environment
from domain import *
import os
import hash
import ingester

def feed_jellyfin_items():
    url = f"http://localhost:8096/items?apikey={environment.JELLY_APIKEY}&recursive=true&fields=ProviderIds,Path"

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
            
            s.sha512 = hash.get_audio_hash_sha512(s.path)

            if SourceService.do_source_exists(conn, s.sha512, s.imdb_id):   
                print(f"Source already exists: {s.imdb_id} - {s.path}")
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

if __name__ == "__main__":
    feed_jellyfin_items()