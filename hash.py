import subprocess
import hashlib
from pathlib import Path

FFMPEG_BIN = Path(__file__).parent / "dep" / "ffmpeg" / "ffmpeg.exe"

def get_audio_hash_sha512(file_path: str) -> str:
    ffmpeg_cmd = [
        str(FFMPEG_BIN),
        "-loglevel", "error",
        "-i", file_path,
        "-map_metadata", "-1",
        "-f", "wav",
        "-"
    ]

    sha512_hash = hashlib.sha512()

    with subprocess.Popen(
        ffmpeg_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ) as proc:
        assert proc.stdout is not None

        while chunk := proc.stdout.read(65536):
            sha512_hash.update(chunk)

        stderr = proc.stderr.read() if proc.stderr else b""
        return_code = proc.wait()

        if return_code != 0:
            raise RuntimeError(
                f"Error en ffmpeg: {stderr.decode(errors='replace').strip()}"
            )

    return sha512_hash.hexdigest()

if __name__ == "__main__":
    try:
        archivo = r"D:\Videos\Movies\Good Will Hunting (1997) [1080p]\Good.Will.Hunting.1997.1080p.BrRip.x264.YIFY.mp4"
        hash_resultado = get_audio_hash_sha512(archivo)
        print(f"SHA-512 del audio puro: {hash_resultado}")
    except Exception as error:
        print(f"Error: {error}")
