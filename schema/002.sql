-- extra color modes (see ColorMode in domain.py), one row per source and mode;
-- colors holds 3 bytes (r, g, b) per frame, in frame_index order

CREATE TABLE SourceColors (
    id INTEGER PRIMARY KEY,
    source_id INTEGER,
    color_mode INTEGER,
    colors BLOB,
    FOREIGN KEY(source_id) REFERENCES Source(id)
);

CREATE UNIQUE INDEX index_sourcecolors_sourceid_colormode ON SourceColors(source_id, color_mode);
