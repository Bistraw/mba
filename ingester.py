from pathlib import Path
import subprocess
import render
import domain

FFMPEG_BIN = Path(__file__).parent / "dep" / "ffmpeg" / "ffmpeg.exe"

def ingest(file_path) -> list[domain.Color]:
    # leer el archivo (file_path)
    cmd = [
        str(FFMPEG_BIN),
        "-v", "error",
        "-i", str(file_path),
        "-an",                                  # ignore audio
        "-vf", "scale=1:1:flags=area",          # mean color of each frame -> 1 pixel
        "-pix_fmt", "rgb24",
        "-f", "rawvideo",
        "pipe:1",
    ]
    # por cada frame calcula el color promedio
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="replace"))

    raw = proc.stdout
    colors: list[domain.Color] = []
    for i in range(0, len(raw) - 2, 3):
        r, g, b = raw[i], raw[i + 1], raw[i + 2]
        colors.append(domain.Color(r, g, b))

    return colors

if __name__ == "__main__":
    file_path = r"D:\Videos\Movies\[MTBB] Mushoku Tensei (BD 1080p)\[MTBB] Mushoku Tensei - 01v3 [0C3C916A].mkv"
    #file_path = r"D:\Videos\Movies\Black Swan (2010) [1080p] [BluRay] [5.1] [YTS.MX]\Black.Swan.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"
        
    data : list[domain.Color] = ingest(file_path)

    #img = render.render(data, 1920, 1080)
    img = render.render_force_max_lines(data, 5, 5000)

    img.show()