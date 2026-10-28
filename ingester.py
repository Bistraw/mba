from pathlib import Path
import subprocess
import numpy as np
import render
import domain
from domain import ColorMode

FFMPEG_BIN = Path(__file__).parent / "dep" / "ffmpeg" / "ffmpeg.exe"

# each frame is shrunk to this size (area average) before it's analyzed,
# so a single noisy/highlight pixel doesn't win; 64x36 keeps 16:9 and divides 1920x1080 exactly
SAMPLE_W = 64
SAMPLE_H = 36

FRAME_SIZE = SAMPLE_W * SAMPLE_H * 3   # rgb24
CHUNK_FRAMES = 2000                    # frames processed per numpy batch (~14 MB)

# Rec. 709 luma weights, "brightness" as perceived by the eye
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

HIGHLIGHTS_SHARE = 0.10     # share of the brightest pixels averaged by HIGHLIGHTS
DOMINANT_BITS = 3           # bits kept per channel by DOMINANT, 3 -> 8x8x8 = 512 bins
HUE_MIN_SATURATION = 0.08   # below this HUE treats the frame as gray

def _to_u8(values : np.ndarray) -> np.ndarray:
    return np.clip(np.rint(values), 0, 255).astype(np.uint8)

def _dominant(pixels : np.ndarray) -> np.ndarray:
    # mean color of the most populated bin of each frame
    n, p, _ = pixels.shape
    bins = 1 << (3 * DOMINANT_BITS)
    shift = 8 - DOMINANT_BITS

    q = (pixels >> shift).astype(np.int64)
    idx = (q[..., 0] << (2 * DOMINANT_BITS)) | (q[..., 1] << DOMINANT_BITS) | q[..., 2]
    idx += (np.arange(n) * bins)[:, None]   # each frame gets its own range of bins

    flat = idx.ravel()
    counts = np.bincount(flat, minlength=n * bins).reshape(n, bins)
    best = counts.argmax(axis=1)

    rows = np.arange(n)
    result = np.empty((n, 3), dtype=np.float64)

    for c in range(3):
        sums = np.bincount(flat, weights=pixels[..., c].ravel(), minlength=n * bins).reshape(n, bins)
        result[:, c] = sums[rows, best] / counts[rows, best]

    return _to_u8(result)

def _pure_hue(avg : np.ndarray) -> np.ndarray:
    # the hue of each color at full saturation and value, grays stay gray
    rgb = avg.astype(np.float32) / 255
    mx = rgb.max(axis=1)
    mn = rgb.min(axis=1)
    chroma = mx - mn

    safe = np.where(chroma == 0, 1, chroma)
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]

    h = np.where(mx == r, ((g - b) / safe) % 6,
        np.where(mx == g, (b - r) / safe + 2, (r - g) / safe + 4))

    # hsv -> rgb with s = v = 1
    k = (np.stack([5 + h, 3 + h, 1 + h], axis=1)) % 6
    pure = 1 - np.clip(np.minimum(k, 4 - k), 0, 1)

    saturation = np.where(mx == 0, 0, chroma / np.where(mx == 0, 1, mx))
    gray = (rgb @ LUMA)[:, None].repeat(3, axis=1)

    return _to_u8(np.where((saturation < HUE_MIN_SATURATION)[:, None], gray, pure) * 255)

def _frames_stats(raw : bytes) -> dict[int, np.ndarray]:
    # raw holds n whole frames of SAMPLE_W x SAMPLE_H rgb24 pixels, returns an (n, 3) uint8 array per color mode
    n = len(raw) // FRAME_SIZE

    pixels = np.frombuffer(raw, dtype=np.uint8, count=n * FRAME_SIZE).reshape(n, SAMPLE_W * SAMPLE_H, 3)
    pixels_f = pixels.astype(np.float32)
    rows = np.arange(n)

    luma = pixels_f @ LUMA
    chroma = pixels.max(axis=2).astype(np.int16) - pixels.min(axis=2)

    avg = _to_u8(pixels_f.mean(axis=1))

    # brightest 10% of each frame
    k = int(pixels.shape[1] * (1 - HIGHLIGHTS_SHARE))
    top = np.argpartition(luma, k, axis=1)[:, k:]

    grid = pixels_f.reshape(n, SAMPLE_H, SAMPLE_W, 3)
    center = grid[:, SAMPLE_H // 3 : 2 * SAMPLE_H // 3, SAMPLE_W // 3 : 2 * SAMPLE_W // 3]

    return {
        ColorMode.AVERAGE: avg,
        ColorMode.BRIGHTEST: pixels[rows, luma.argmax(axis=1)],
        ColorMode.VIVID: pixels[rows, chroma.argmax(axis=1)],
        ColorMode.DOMINANT: _dominant(pixels),
        ColorMode.MEDIAN: _to_u8(np.median(pixels, axis=1)),
        ColorMode.CENTER: _to_u8(center.mean(axis=(1, 2))),
        ColorMode.HIGHLIGHTS: _to_u8(np.take_along_axis(pixels_f, top[..., None], axis=1).mean(axis=1)),
        ColorMode.HUE: _pure_hue(avg),
        ColorMode.LUMINANCE: _to_u8((avg.astype(np.float32) @ LUMA)[:, None].repeat(3, axis=1)),
    }

def ingest_colors(file_path) -> dict[int, np.ndarray]:
    # every color mode of every frame from a single ffmpeg pass, as {mode: (frames, 3) uint8 array}
    cmd = [
        str(FFMPEG_BIN),
        "-v", "error",
        "-i", str(file_path),
        "-an",                                              # ignore audio
        "-vf", f"scale={SAMPLE_W}:{SAMPLE_H}:flags=area",   # small version of each frame
        "-pix_fmt", "rgb24",
        "-f", "rawvideo",
        "pipe:1",
    ]

    chunks : list[dict[int, np.ndarray]] = []

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        assert proc.stdout is not None

        while raw := proc.stdout.read(FRAME_SIZE * CHUNK_FRAMES):
            if len(raw) >= FRAME_SIZE:
                chunks.append(_frames_stats(raw))

        stderr = proc.stderr.read() if proc.stderr else b""

        if proc.wait() != 0:
            raise RuntimeError(stderr.decode(errors="replace"))

    return {mode: np.concatenate([c[mode] for c in chunks]) if chunks else np.empty((0, 3), dtype=np.uint8)
            for mode, _, _ in ColorMode.ALL}

def to_colors(values : np.ndarray) -> list[domain.Color]:
    return [domain.Color(int(r), int(g), int(b)) for r, g, b in values]

def ingest(file_path, color_mode : int = ColorMode.AVERAGE) -> list[domain.Color]:
    # one color per frame for the given mode
    return to_colors(ingest_colors(file_path)[color_mode])

def ingest_brightest(file_path) -> list[domain.Color]:
    # brightest color of each frame
    return ingest(file_path, ColorMode.BRIGHTEST)

if __name__ == "__main__":
    file_path = r"D:\Videos\Movies\[MTBB] Mushoku Tensei (BD 1080p)\[MTBB] Mushoku Tensei - 01v3 [0C3C916A].mkv"
    #file_path = r"D:\Videos\Movies\Black Swan (2010) [1080p] [BluRay] [5.1] [YTS.MX]\Black.Swan.2010.1080p.BluRay.x264.AAC5.1-[YTS.MX].mp4"

    data : list[domain.Color] = ingest(file_path, ColorMode.VIVID)

    #img = render.render(data, 1920, 1080)
    img = render.render_force_max_lines(data, 5, 5000)

    img.show()
