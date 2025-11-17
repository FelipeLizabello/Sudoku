import sys
import os
import math
import random
import time
import pygame as pg
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.graph.generator import gerar_tabuleiro

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


connections = None
tabuleiro = None
solucao = None
_ = None

show_solution = False
# Animation state for revealing the rest of the board
animated_board = None
fill_positions = []
reveal_index = 0
reveal_start_time = 0.0
reveal_interval = 0.05  # seconds between revealing cells
reveal_active = False

conflict_highlights = []
conflict_duration = 0.8

status_message = ""
status_message_expire = 0.0
status_message_color = (200, 220, 230)
STATUS_MESSAGE_DURATION = 3.0


def is_move_valid(row, col, value, board_state=None):
    """Return True if placing `value` at (row,col) doesn't conflict with neighbors.
    Uses the `connections` adjacency mapping produced by the generator.
    If board_state is None uses the global `tabuleiro`.
    """
    if value == 0:
        return True
    if board_state is None:
        board_state = tabuleiro
    neighs = connections.get((row, col), set()) if connections is not None else set()
    for n in neighs:
        r, c = n
        if board_state[r][c] == value:
            return False
    return True


def get_candidates(row, col, board_state=None):
    """Return a sorted list of possible values (1..9) that don't conflict at (row,col)."""
    if board_state is None:
        board_state = tabuleiro
    used = set()
    neighs = connections.get((row, col), set()) if connections is not None else set()
    for n in neighs:
        r, c = n
        v = board_state[r][c]
        if v != 0:
            used.add(v)
    return [v for v in range(1, 10) if v not in used]


def _highlight_conflict_at(row, col, value):
    """Register conflict highlight for attempted invalid placement at (row,col)
    and any neighbors that contain the conflicting value."""
    now = time.time()
    expire = now + conflict_duration
    conflict_highlights.append((row, col, expire))
    neighs = connections.get((row, col), set()) if connections is not None else set()
    for r, c in neighs:
        if tabuleiro[r][c] == value:
            conflict_highlights.append((r, c, expire))


def _set_status_message(text, color, duration=STATUS_MESSAGE_DURATION):
    global status_message, status_message_color, status_message_expire
    status_message = text
    status_message_color = color
    status_message_expire = time.time() + duration


def validate_current_board():
    if tabuleiro is None or connections is None:
        return False, "Tabuleiro indisponível."
    for r in range(9):
        for c in range(9):
            valor = tabuleiro[r][c]
            if valor not in range(1, 10):
                return False, "Ainda há casas vazias ou inválidas."
            for nr, nc in connections.get((r, c), set()):
                if (nr, nc) <= (r, c):
                    continue
                if tabuleiro[nr][nc] == valor:
                    return False, "Existem conflitos no tabuleiro."
    return True, "Tabuleiro correto! Parabéns."


def start_fill_animation(interval=0.05, random_order=False):
    """Inicializa o estado para animar o preenchimento das casas vazias.
    Por padrão ordena em leitura (linha-major). Se random_order=True,
    embaralha a ordem de revelação.
    """
    global animated_board, fill_positions, reveal_index, reveal_start_time, reveal_interval, reveal_active
    if tabuleiro is None or solucao is None:
        return
    animated_board = [row[:] for row in tabuleiro]
    # posições que estão vazias no puzzle original
    fill_positions = [(i, j) for i in range(9) for j in range(9) if tabuleiro[i][j] == 0]
    if random_order:
        random.shuffle(fill_positions)
    reveal_index = 0
    reveal_start_time = time.time()
    reveal_interval = interval
    reveal_active = True


def stop_fill_animation():
    global reveal_active
    reveal_active = False


# --- Interaction state (for 'Jogar' mode) ---
# set of coordinates which are presets (non-editable)
preset_positions = set()
# currently selected cell (row, col)
selected_cell = (0, 0)



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

    cell = inner.width // 9
    try:
        font = pg.font.SysFont("couriernew", 44, bold=True)
    except Exception:
        font = pg.font.SysFont(None, 44, bold=True)

    # Choose which board to display: the puzzle or the full solution
    # Determine display board depending on animation state
    global animated_board, reveal_active, reveal_index, reveal_start_time, fill_positions

    if reveal_active and animated_board is not None:
        # update how many cells should be revealed based on elapsed time
        elapsed = time.time() - reveal_start_time
        should_reveal = min(len(fill_positions), int(elapsed / reveal_interval))
        # reveal progressively
        while reveal_index < should_reveal:
            i, j = fill_positions[reveal_index]
            # obtain solution value (support dict or 2D list)
            if isinstance(solucao, dict):
                v = solucao.get((i, j), 0)
            else:
                v = solucao[i][j]
            animated_board[i][j] = v
            reveal_index += 1

        display_tabuleiro = animated_board

        # if finished, stop animation
        if reveal_index >= len(fill_positions):
            reveal_active = False
    else:
        if show_solution:
            # generator can return solution as a dict mapping (i,j)->value
            if isinstance(solucao, dict):
                display_tabuleiro = [[solucao.get((i, j), 0) for j in range(9)] for i in range(9)]
            else:
                display_tabuleiro = solucao
        else:
            display_tabuleiro = tabuleiro

    # Draw selection highlight if in play mode (not showing full solution)
    try:
        global selected_cell, preset_positions
    except Exception:
        selected_cell = (0, 0)
        preset_positions = set()

    if not show_solution:
        sel_r, sel_c = selected_cell
        # clamp
        sel_r = max(0, min(8, sel_r))
        sel_c = max(0, min(8, sel_c))
        sel_x = inner.x + sel_c * cell
        sel_y = inner.y + sel_r * cell
        sel_rect = pg.Rect(sel_x, sel_y, cell, cell)
        # translucent overlay
        overlay = pg.Surface((cell, cell), flags=pg.SRCALPHA)
        overlay.fill((40, 220, 200, 30))
        screen.blit(overlay, (sel_x, sel_y))
        # border
        pg.draw.rect(screen, (40, 220, 200), sel_rect, 3)

    for i in range(9):
        for j in range(9):
            valor = display_tabuleiro[i][j]
            if valor != 0:
                # preset numbers (given by generator) are drawn in a slightly different color
                if (i, j) in preset_positions:
                    color = (180, 240, 200)
                else:
                    color = (220, 240, 220)
                text = font.render(str(valor), True, color)
                x = inner.x + j * cell + cell // 2 - text.get_width() // 2
                y = inner.y + i * cell + cell // 2 - text.get_height() // 2
                screen.blit(text, (x, y))

    # draw conflict highlights (fade out over time)
    now = time.time()
    remaining = []
    for (r, c, exp) in conflict_highlights:
        if exp > now:
            remaining.append((r, c, exp))
            alpha = int(200 * ((exp - now) / conflict_duration))
            cx = inner.x + c * cell
            cy = inner.y + r * cell
            surf = pg.Surface((cell, cell), flags=pg.SRCALPHA)
            surf.fill((230, 50, 50, max(30, alpha)))
            screen.blit(surf, (cx, cy))
            pg.draw.rect(screen, (230, 50, 50), pg.Rect(cx, cy, cell, cell), 3)
    # keep only non-expired
    conflict_highlights[:] = remaining

    if status_message and now < status_message_expire:
        try:
            msg_font = pg.font.SysFont("couriernew", 28, bold=True)
        except Exception:
            msg_font = pg.font.SysFont(None, 28, bold=True)
        msg_surf = msg_font.render(status_message, True, status_message_color)
        screen.blit(msg_surf, (board_x + 20, inner.bottom - msg_surf.get_height() - 12))


def game_loop():
    global selected_cell, preset_positions, tabuleiro

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # Navigation and number input only when NOT showing the solved board
        if not show_solution:
            if event.type == pg.KEYDOWN:
                r, c = selected_cell
                # arrow keys
                if event.key == pg.K_UP:
                    r = (r - 1) % 9
                elif event.key == pg.K_DOWN:
                    r = (r + 1) % 9
                elif event.key == pg.K_LEFT:
                    c = (c - 1) % 9
                elif event.key == pg.K_RIGHT:
                    c = (c + 1) % 9
                # numeric keys (0-9) - include keypad
                elif event.unicode and event.unicode in '0123456789':
                    val = int(event.unicode)
                    if (r, c) not in preset_positions:
                        if val == 0:
                            tabuleiro[r][c] = 0
                        else:
                            tabuleiro[r][c] = val
                elif event.key in (pg.K_KP0, pg.K_KP1, pg.K_KP2, pg.K_KP3, pg.K_KP4, pg.K_KP5, pg.K_KP6, pg.K_KP7, pg.K_KP8, pg.K_KP9):
                    # keypad keys - map to digit
                    kp_map = {
                        pg.K_KP0: 0, pg.K_KP1: 1, pg.K_KP2: 2, pg.K_KP3: 3, pg.K_KP4: 4,
                        pg.K_KP5: 5, pg.K_KP6: 6, pg.K_KP7: 7, pg.K_KP8: 8, pg.K_KP9: 9,
                    }
                    val = kp_map.get(event.key, None)
                    if val is not None and (r, c) not in preset_positions:
                        if val == 0:
                            tabuleiro[r][c] = 0
                        else:
                            tabuleiro[r][c] = val

                selected_cell = (r, c)

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # allow clicking to select a cell
                mx, my = event.pos
                # compute inner board area same as in draw_board
                board_x = 280
                board_y = 10
                inner = pg.Rect(board_x + 10, board_y + 10, 700, 700)
                if inner.collidepoint(mx, my):
                    cell = inner.width // 9
                    col = (mx - inner.x) // cell
                    row = (my - inner.y) // cell
                    if 0 <= row < 9 and 0 <= col < 9:
                        selected_cell = (row, col)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                success, msg = validate_current_board()
                color = (120, 230, 160) if success else (230, 120, 120)
                _set_status_message(msg, color)

    draw_board()
    pg.display.flip()
    clock.tick(60)


if __name__ == '__main__':
    while True:
        game_loop()

        draw_board()
        pg.display.flip()
        clock.tick(60)


def draw_menu(selected=0):
    """Desenha a tela de menu. `selected` é o índice da opção destacada."""
    t = time.time()
    draw_starfield(screen, t)

    # panel
    w, h = screen_size
    menu_rect = pg.Rect(w // 2 - 380, h // 2 - 200, 760, 400)
    panel = pg.Surface((menu_rect.width, menu_rect.height), flags=pg.SRCALPHA)
    panel.fill((8, 10, 25, 230))
    screen.blit(panel, (menu_rect.x, menu_rect.y))
    neon_rect(screen, menu_rect, (40, 220, 200), glow_size=20, border=6)

    try:
        title_font = pg.font.SysFont("couriernew", 72, bold=True)
        opt_font = pg.font.SysFont("couriernew", 48, bold=True)
    except Exception:
        title_font = pg.font.SysFont(None, 72, bold=True)
        opt_font = pg.font.SysFont(None, 48, bold=True)

    title_surf = title_font.render("S U D O K U", True, (140, 240, 220))
    screen.blit(title_surf, (menu_rect.x + 40, menu_rect.y + 20))

    # opções
    opts = ["Jogar", "Ver resolução"]
    base_y = menu_rect.y + 140
    opt_h = 80
    rects = []
    for i, o in enumerate(opts):
        r = pg.Rect(menu_rect.x + 80, base_y + i * (opt_h + 20), menu_rect.width - 160, opt_h)
        rects.append(r)
        color = (40, 220, 200) if i == selected else (70, 100, 140)
        neon_rect(screen, r, color, glow_size=10, border=4)
        txt = opt_font.render(o, True, (20, 20, 30) if i == selected else (180, 220, 230))
        screen.blit(txt, (r.x + 24, r.y + r.height // 2 - txt.get_height() // 2))

    # instruções
    try:
        small = pg.font.SysFont("couriernew", 20)
    except Exception:
        small = pg.font.SysFont(None, 20)
    inst = small.render("Use as setas ou clique. Enter seleciona. Esc sai.", True, (180, 200, 220))
    screen.blit(inst, (menu_rect.x + 40, menu_rect.bottom - 40))

    return rects


def menu_loop():
    """Mostra a tela de menu e retorna 'play' ou 'solution' (ou None se sair)."""
    selected = 0
    rects = draw_menu(selected)
    pg.display.flip()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(0)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit(0)
                if event.key in (pg.K_UP, pg.K_w):
                    selected = (selected - 1) % 2
                if event.key in (pg.K_DOWN, pg.K_s):
                    selected = (selected + 1) % 2
                if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                    return 'play' if selected == 0 else 'solution'
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        return 'play' if i == 0 else 'solution'

        # atualizar desenho
        rects = draw_menu(selected)
        pg.display.flip()
        clock.tick(60)
