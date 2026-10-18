CREATE TABLE Settings(  
    id INTEGER PRIMARY KEY,
    key VARCHAR(255),
    value VARCHAR(255)
);

CREATE TABLE Source (
    id INTEGER PRIMARY KEY,
    sha512 VARCHAR(128),
    imdb_id VARCHAR(10),
    kind INTEGER,
    metadata_name TEXT,
    metadata_year INTEGER
);

CREATE UNIQUE INDEX index_source_sha512 ON Source(sha512);
CREATE UNIQUE INDEX index_source_imdbid ON Source(imdb_id);

CREATE TABLE SourceFrame (
    id INTEGER PRIMARY KEY,
    source_id INTEGER, 
    frame_index INTEGER,
    color_r INTEGER,
    color_g INTEGER,
    color_b INTEGER,
    FOREIGN KEY(source_id) REFERENCES Source(id)
);  

CREATE UNIQUE INDEX index_sourceframe_sourceid_frameindex ON SourceFrame(source_id, frame_index);

INSERT INTO Settings(key, value) VALUES('db_version', '000');