"""Generate anime-style icon for MultiSourceReportTool."""

import io
import math
import struct

from PIL import Image, ImageDraw, ImageFilter

SIZE = 256
OUTPUT = "resources/app_icon.ico"


def create_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size / 2 - 4

    # --- Background circle gradient ---
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= r:
                t = dist / r
                # Pink (#f472b6) -> Purple (#a78bfa) -> darker at edges
                rr = int(244 - 80 * t - 30 * (t**2))
                gg = int(114 + 25 * t - 40 * (t**2))
                bb = int(182 - 40 * t + 70 * (t**2))
                alpha = 255
                img.putpixel(
                    (x, y),
                    (max(0, min(255, rr)), max(0, min(255, gg)), max(0, min(255, bb)), alpha),
                )

    # --- Soft blur background ---
    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    draw = ImageDraw.Draw(img)

    # --- White inner circle for depth ---
    inner_r = max(1, r - 12)
    if inner_r > 0:
        draw.ellipse(
            [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=(255, 255, 255, 40)
        )

    # --- Cute document body (rounded rect) ---
    doc_w, doc_h = 90, 110
    doc_x1 = cx - doc_w / 2
    doc_y1 = cy - doc_h / 2 - 8
    doc_x2 = cx + doc_w / 2
    doc_y2 = cy + doc_h / 2 - 8

    # Document shadow
    draw.rounded_rectangle(
        [doc_x1 + 3, doc_y1 + 3, doc_x2 + 3, doc_y2 + 3], radius=12, fill=(0, 0, 0, 50)
    )
    # Document body - white with slight pink tint
    draw.rounded_rectangle(
        [doc_x1, doc_y1, doc_x2, doc_y2],
        radius=12,
        fill=(255, 250, 252, 255),
        outline=(236, 180, 200, 255),
        width=2,
    )

    # --- Document lines (text lines look) ---
    line_color = (220, 200, 210, 200)
    line_y_start = doc_y1 + 30
    for i in range(5):
        ly = line_y_start + i * 14
        line_w = doc_w - 30 if i < 4 else doc_w - 50
        lx1 = doc_x1 + 15
        draw.rounded_rectangle([lx1, ly, lx1 + line_w, ly + 5], radius=2, fill=line_color)

    # --- Glasses / cute eyes on the document ---
    eye_y = doc_y1 + 36
    # Left eye
    eye_lx = cx - 16
    _draw_anime_eye(draw, eye_lx, eye_y, 12)
    # Right eye
    eye_rx = cx + 16
    _draw_anime_eye(draw, eye_rx, eye_y, 12)

    # --- Blush marks ---
    blush_y = eye_y + 18
    for bx in [cx - 22, cx + 22]:
        blush = Image.new("RGBA", (20, 10), (0, 0, 0, 0))
        blush_d = ImageDraw.Draw(blush)
        blush_d.ellipse([0, 0, 20, 10], fill=(255, 180, 190, 100))
        blush = blush.filter(ImageFilter.GaussianBlur(radius=3))
        img.paste(blush, (int(bx - 10), int(blush_y - 5)), blush)

    # --- Small mouth ---
    mouth_y = blush_y + 8
    draw.arc(
        [cx - 5, mouth_y, cx + 5, mouth_y + 8], start=0, end=180, fill=(200, 130, 150, 180), width=2
    )

    # --- Sparkle decorations ---
    sparkle_positions = [
        (cx - 65, cy - 55, 8),
        (cx + 70, cy - 35, 6),
        (cx - 55, cy + 70, 7),
        (cx + 60, cy + 60, 5),
        (cx - 80, cy + 10, 5),
        (cx + 80, cy - 10, 6),
    ]
    for sx, sy, sz in sparkle_positions:
        _draw_sparkle(draw, sx, sy, sz)

    # --- Top-left star ---
    _draw_star(draw, cx + 55, cy - 78, 10, (255, 255, 200, 220))
    _draw_star(draw, cx - 60, cy + 80, 8, (255, 230, 200, 200))

    # --- Bokeh circles ---
    for bx, by, br, ba in [
        (cx - 75, cy - 70, 14, 60),
        (cx + 85, cy + 50, 10, 50),
        (cx - 40, cy - 85, 6, 70),
        (cx + 45, cy + 80, 8, 55),
    ]:
        bokeh = Image.new("RGBA", (br * 3, br * 3), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bokeh)
        bd.ellipse([br, br, br * 2, br * 2], fill=(255, 255, 255, ba))
        bokeh = bokeh.filter(ImageFilter.GaussianBlur(radius=br / 3))
        img.paste(bokeh, (int(bx - br * 1.5), int(by - br * 1.5)), bokeh)

    # --- Outer glow ring ---
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_d = ImageDraw.Draw(glow)
    glow_d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 200, 220, 80), width=3)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, glow)

    return img


def _draw_anime_eye(draw, cx, cy, size):
    """Draw a single anime-style eye."""
    # White base
    draw.ellipse(
        [cx - size, cy - size * 0.9, cx + size, cy + size * 0.9],
        fill=(255, 255, 255, 255),
        outline=(120, 100, 110, 255),
        width=2,
    )
    # Iris (large pupil - anime style)
    iris_r = size * 0.7
    draw.ellipse(
        [cx - iris_r, cy - iris_r * 0.7, cx + iris_r, cy + iris_r * 0.7], fill=(80, 60, 90, 255)
    )
    # Pupil
    pupil_r = size * 0.4
    draw.ellipse(
        [cx - pupil_r, cy - pupil_r * 0.6, cx + pupil_r, cy + pupil_r * 0.6], fill=(30, 20, 35, 255)
    )
    # Highlight 1 (big)
    draw.ellipse(
        [cx - size * 0.2, cy - size * 0.35, cx + size * 0.5, cy + size * 0.35],
        fill=(255, 255, 255, 240),
    )
    # Highlight 2 (small)
    draw.ellipse(
        [cx - size * 0.1, cy + size * 0.1, cx + size * 0.2, cy + size * 0.4],
        fill=(255, 255, 255, 150),
    )
    # Upper eyelid line (thicker)
    draw.arc(
        [cx - size - 1, cy - size * 0.7, cx + size + 1, cy + size * 0.3],
        start=200,
        end=340,
        fill=(60, 45, 65, 255),
        width=2,
    )


def _draw_sparkle(draw, cx, cy, size):
    """Draw a four-point sparkle."""
    points = [
        (cx, cy - size),  # top
        (cx + size * 0.35, cy - size * 0.2),  # right-inner-top
        (cx + size, cy),  # right
        (cx + size * 0.35, cy + size * 0.2),  # right-inner-bottom
        (cx, cy + size),  # bottom
        (cx - size * 0.35, cy + size * 0.2),  # left-inner-bottom
        (cx - size, cy),  # left
        (cx - size * 0.35, cy - size * 0.2),  # left-inner-top
    ]
    draw.polygon(points, fill=(255, 255, 255, 230))
    # Center glow
    draw.ellipse(
        [cx - size * 0.15, cy - size * 0.15, cx + size * 0.15, cy + size * 0.15],
        fill=(255, 255, 255, 255),
    )


def _draw_star(draw, cx, cy, size, color):
    """Draw a 5-pointed star."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.4
        px = cx + r * math.cos(angle)
        py = cy - r * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=color)


def save_multi_ico(images, sizes, filepath):
    """Save multiple resolutions into a single .ico file manually."""
    png_list = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_list.append(buf.getvalue())

    num = len(images)
    header = struct.pack("<HHH", 0, 1, num)
    offset = 6 + 16 * num
    entries = b""
    data = b""

    for size, png in zip(sizes, png_list, strict=False):
        w, h = size
        if w >= 256:
            w = 0
        if h >= 256:
            h = 0
        entry = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), offset)
        entries += entry
        data += png
        offset += len(png)

    with open(filepath, "wb") as f:
        f.write(header + entries + data)


if __name__ == "__main__":
    master = create_icon(SIZE)
    size_list = [16, 24, 32, 48, 64, 128, 256]
    frames = [master.resize((s, s), Image.LANCZOS) for s in size_list]
    size_pairs = [(s, s) for s in size_list]
    save_multi_ico(frames, size_pairs, OUTPUT)
    print(f"Icon saved to {OUTPUT}")
    # Verify
    img = Image.open(OUTPUT)
    count = 0
    while True:
        try:
            img.seek(count)
            count += 1
        except EOFError:
            break
    print(f"Embedded {count} icon sizes")
