import sys
import os
import math
import random
import time
import pygame as pg

pg.init()
screen_size = 1280, 720
screen = pg.display.set_mode(screen_size)
import sys
import os
import math
import random
import time
import pygame as pg

pg.init()
screen_size = 1280, 720
screen = pg.display.set_mode(screen_size)
clock = pg.time.Clock()

# Try to load a background image from likely locations (keeps existing behavior)
image_paths = [
    os.path.join(os.path.dirname(__file__), "..", "assets", "background.jpg"),
    os.path.join(os.path.dirname(__file__), "..", "assets", "background.png"),
    os.path.join(os.path.dirname(__file__), "assets", "background.jpg"),
    os.path.join(os.path.dirname(__file__), "assets", "background.png"),
]

background_image = None
for path in image_paths:
    try:
        if os.path.exists(path):
            background_image = pg.image.load(path).convert()
            background_image = pg.transform.scale(background_image, screen_size)
            break
    except Exception:
        background_image = None


# ------------------ Starfield ------------------
NUM_STARS = 120
stars = []
for _ in range(NUM_STARS):
    stars.append({
        "x": random.uniform(0, screen_size[0]),
        "y": random.uniform(0, screen_size[1]),
        "z": random.uniform(0.2, 1.0),
        "phase": random.uniform(0, math.pi * 2),
    })


def draw_starfield(surface, t):
    # base dark space
    surface.fill((6, 6, 20))

    # optional background image blended under stars
    if background_image:
        surface.blit(background_image, (0, 0))
        overlay = pg.Surface(screen_size, flags=pg.SRCALPHA)
        overlay.fill((0, 0, 20, 120))
        surface.blit(overlay, (0, 0))

    # stars
    for s in stars:
        speed = (1.0 - s["z"]) * 40.0
        s["x"] -= speed * 0.016
        if s["x"] < 0:
            s["x"] = screen_size[0]
            s["y"] = random.uniform(0, screen_size[1])
            s["z"] = random.uniform(0.2, 1.0)

        tw = (math.sin(t * 4 + s["phase"]) + 1) * 0.5
        base_brightness = int(180 * (1.0 - s["z"]))
        brightness = min(255, int(base_brightness + tw * 75))
        col = (brightness, brightness, brightness)
        radius = 1 if s["z"] > 0.7 else 2 if s["z"] > 0.4 else 3
        pg.draw.circle(surface, col, (int(s["x"]), int(s["y"])), radius)


# ------------------ Utilities for polylines ------------------


def _segment_info(points):
    seg_lengths = []
    cum = [0.0]
    total = 0.0
    for i in range(len(points) - 1):
        a = points[i]
        b = points[i + 1]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        seg_lengths.append(d)
        total += d
        cum.append(total)
    return seg_lengths, cum, total


def _draw_partial_polyline(surf, pts, cum, seg_lengths, draw_up_to, color, width):
    if draw_up_to <= 0:
        return
    for i in range(len(pts) - 1):
        seg_start = cum[i]
        seg_end = cum[i + 1]
        a = pts[i]
        b = pts[i + 1]
        if seg_start >= draw_up_to:
            break
        if seg_end <= draw_up_to:
            pg.draw.line(surf, color, a, b, width)
        else:
            remain = draw_up_to - seg_start
            if seg_lengths[i] == 0:
                continue
            t = remain / seg_lengths[i]
            ix = a[0] + (b[0] - a[0]) * t
            iy = a[1] + (b[1] - a[1]) * t
            pg.draw.line(surf, color, a, (int(ix), int(iy)), width)


# ------------------ Lightning (literal bolts top -> bottom) ------------------
lightning_events = []  # list of events
LIGHTNING_MAX = 2


def generate_bolt(x_center=None, width=screen_size[0], height=screen_size[1]):
    # create jagged main bolt from top to bottom
    if x_center is None:
        x = random.uniform(120, width - 120)
    else:
        x = x_center
    points = []
    y = 0
    cur_x = x
    while y < height:
        points.append((cur_x + random.uniform(-6, 6), y))
        y += random.randint(24, 64)
        cur_x += random.uniform(-90, 90)
        cur_x = max(50, min(width - 50, cur_x))
    points.append((cur_x, height))

    seg_lengths, cum, total = _segment_info(points)

    branches = []
    for _ in range(random.randint(1, 4)):
        anchor = random.randint(1, max(1, len(points) - 3))
        ax, ay = points[anchor]
        bpoints = [(ax, ay)]
        steps = random.randint(3, 6)
        angle = random.choice([-1, 1])
        for i in range(steps):
            bx = bpoints[-1][0] + angle * random.uniform(40, 140)
            by = bpoints[-1][1] + random.uniform(10, 80)
            bx = max(20, min(width - 20, bx))
            bpoints.append((bx, by))
        bseg_lengths, bcum, btotal = _segment_info(bpoints)
        branches.append({
            "anchor": anchor,
            "points": bpoints,
            "seg_lengths": bseg_lengths,
            "cum": bcum,
            "length": btotal,
            "delay": random.uniform(0.05, 0.25),
        })

    duration = random.uniform(0.35, 0.45)
    speed = total / duration

    return {
        "points": points,
        "seg_lengths": seg_lengths,
        "cum": cum,
        "length": total,
        "branches": branches,
        "created": 0.0,
        "speed": speed,
        "duration": duration,
    }


def draw_bolt(surface, event, elapsed):
    # elapsed seconds since creation
    distance = min(event["length"], elapsed * event["speed"])

    # glow layers: richer cyan -> violet gradient for a dramatic electric look
    glow_layers = [((40, 200, 255, 160), 14), ((160, 80, 220, 110), 8), ((100, 200, 180, 70), 6)]
    for col, w in glow_layers:
        s = pg.Surface(screen_size, flags=pg.SRCALPHA)
        _draw_partial_polyline(s, event["points"], event["cum"], event["seg_lengths"], distance, col, w)
        surface.blit(s, (0, 0), special_flags=pg.BLEND_ADD)

    # bright core (slightly warm-cyan center)
    _draw_partial_polyline(surface, event["points"], event["cum"], event["seg_lengths"], distance, (220, 250, 255), 2)

    # branches with matching palette
    for br in event["branches"]:
        anchor_dist = event["cum"][br["anchor"]]
        if distance <= anchor_dist + br["delay"]:
            continue
        branch_elapsed = distance - anchor_dist - br["delay"]
        branch_draw = min(br["length"], branch_elapsed * (event["speed"] * 0.6))
        bs = pg.Surface(screen_size, flags=pg.SRCALPHA)
        _draw_partial_polyline(bs, br["points"], br["cum"], br["seg_lengths"], branch_draw, (140, 100, 230, 100), 6)
        surface.blit(bs, (0, 0), special_flags=pg.BLEND_ADD)
        _draw_partial_polyline(surface, br["points"], br["cum"], br["seg_lengths"], branch_draw, (220, 250, 255), 2)


# ------------------ Board drawing / UI ------------------


def neon_rect(surface, rect, color, glow_size=14, border=4):
    glow_surf = pg.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), flags=pg.SRCALPHA)
    for i in range(glow_size, 0, -2):
        a = int((1 - i / (glow_size + 1)) * 40)
        r = pg.Rect(glow_size - i // 2, glow_size - i // 2, rect.width + i, rect.height + i)
        pg.draw.rect(glow_surf, (*color, a), r, border)
    pg.draw.rect(glow_surf, (*color, 200), pg.Rect(glow_size, glow_size, rect.width, rect.height), border)
    surface.blit(glow_surf, (rect.x - glow_size, rect.y - glow_size), special_flags=pg.BLEND_PREMULTIPLIED)


def draw_scanlines(surface, spacing=4, alpha=10):
    sl = pg.Surface(screen_size, flags=pg.SRCALPHA)
    sl.fill((0, 0, 0, 0))
    for y in range(0, screen_size[1], spacing):
        pg.draw.line(sl, (0, 0, 0, alpha), (0, y), (screen_size[0], y))
    surface.blit(sl, (0, 0), special_flags=pg.BLEND_RGBA_SUB)


def draw_board():
    t = time.time()
    draw_starfield(screen, t)

    # board area
    board_x = 280
    board_y = 10
    board_size = 720

    panel_rect = pg.Rect(board_x - 10, board_y - 10, board_size + 20, board_size + 20)
    panel_surface = pg.Surface((panel_rect.width, panel_rect.height), flags=pg.SRCALPHA)
    panel_surface.fill((10, 12, 30, 220))
    screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

    neon_color = (40, 220, 200)
    neon_rect(screen, panel_rect, neon_color, glow_size=18, border=6)

    inner = pg.Rect(board_x + 10, board_y + 10, 700, 700)
    pg.draw.rect(screen, (18, 20, 40), inner)
    pg.draw.rect(screen, (22, 26, 50), inner.inflate(-6, -6))

    cell = inner.width // 9
    for i in range(1, 9):
        x = inner.x + i * cell
        y = inner.y + i * cell
        line_color = neon_color if i % 3 == 0 else (100, 180, 220)
        pg.draw.line(screen, (*line_color, 40), (x, inner.y), (x, inner.y + inner.height), 8 if i % 3 == 0 else 4)
        pg.draw.line(screen, (*line_color, 180), (x, inner.y), (x, inner.y + inner.height), 2)
        pg.draw.line(screen, (*line_color, 40), (inner.x, y), (inner.x + inner.width, y), 8 if i % 3 == 0 else 4)
        pg.draw.line(screen, (*line_color, 180), (inner.x, y), (inner.x + inner.width, y), 2)

    pg.draw.rect(screen, neon_color, inner, 3)

    try:
        font = pg.font.SysFont("couriernew", 56, bold=True)
    except Exception:
        font = pg.font.SysFont(None, 56, bold=True)
    title = "S U D O K U"
    title_surf = font.render(title, True, (120, 240, 220))
    for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
        g = font.render(title, True, (12, 40, 50))
        screen.blit(g, (board_x + 20 + dx, board_y - 60 + dy))
    screen.blit(title_surf, (board_x + 20, board_y - 60))

    corner_color = (120, 240, 220)
    pg.draw.circle(screen, corner_color, (inner.x + 10, inner.y + 10), 3)
    pg.draw.circle(screen, corner_color, (inner.right - 10, inner.y + 10), 3)
    pg.draw.circle(screen, corner_color, (inner.x + 10, inner.bottom - 10), 3)
    pg.draw.circle(screen, corner_color, (inner.right - 10, inner.bottom - 10), 3)

    draw_scanlines(screen, spacing=6, alpha=8)

    # --- Lightning spawning and drawing (literal bolts) ---
    # spawn occasionally
    if random.random() < 0.006 and len(lightning_events) < LIGHTNING_MAX:
        b = generate_bolt()
        b["created"] = t
        lightning_events.append(b)

    # render active bolts
    for evt in lightning_events[:]:
        age = t - evt["created"]
        if age * evt["speed"] > evt["length"] + 40:
            try:
                lightning_events.remove(evt)
            except ValueError:
                pass
            continue
        draw_bolt(screen, evt, age)


def game_loop():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    draw_board()
    pg.display.flip()
    clock.tick(60)


if __name__ == '__main__':
    while True:
        game_loop()

        draw_board()
        pg.display.flip()
        clock.tick(60)
