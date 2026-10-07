import os
import time
from PIL import Image
from core.appBase import AppBase
from core.animLoader import get_anims_dir

# <=== {VFD Timer Constants & Segment Mapping} ===>
SLOT_COORDS = [(0, 9), (7, 9), (19, 9), (26, 9)]  # (x, y) origin of each digit slot

# 7-Segment definitions with physical core filament and inner tube glow pixels
SEGMENTS = {
    "a": {
        "core": [(x, 0) for x in range(1, 5)],
        "glow": [(2, 1), (3, 1)]
    },
    "b": {
        "core": [(5, y) for y in range(1, 6)],
        "glow": [(4, y) for y in range(2, 6)]
    },
    "c": {
        "core": [(5, y) for y in range(7, 12)],
        "glow": [(4, y) for y in range(7, 11)]
    },
    "d": {
        "core": [(x, 12) for x in range(1, 5)],
        "glow": [(2, 11), (3, 11)]
    },
    "e": {
        "core": [(0, y) for y in range(7, 12)],
        "glow": [(1, y) for y in range(7, 11)]
    },
    "f": {
        "core": [(0, y) for y in range(1, 6)],
        "glow": [(1, y) for y in range(2, 6)]
    },
    "g": {
        "core": [(x, 6) for x in range(2, 4)],
        "glow": []  # Middle segment g has no inner tube glow
    },
}

DIGITS = {
    "0": "abcdef",
    "1": "bc",
    "2": "abdeg",
    "3": "abcdg",
    "4": "bcfg",
    "5": "acdfg",
    "6": "acdefg",
    "7": "abc",
    "8": "abcdefg",
    "9": "abcdfg"
}

COLON_DOTS = [(15, 12), (15, 17)]  # 2x2 dots

ORANGE_INDICATOR = (24, 27)         # 3x3 square with cross

# Bottom progress bar pixels in left-to-right fill order (16 pixels total)
PROGRESS_PIXELS = [
    (0, 28),
    (2, 28), (3, 28),
    (5, 28), (6, 28),
    (8, 28), (9, 28),
    (11, 28), (12, 28),
    (14, 28), (15, 28),
    (17, 28), (18, 28), (19, 28),
    (18, 27), (18, 29)
]

# Header Bitmaps for all 4 Sessions (32x4 pixels: Title + Session Indicators)
FOCUS_1_HEADER = [
    [None, '#f4721f', '#f5721e', '#f5731f', None, None, '#f5721f', '#f4731e', None, '#f5721f', '#f4721e', None, '#f5721e', None, '#f4731f', None, '#f5731e', '#f5731f', None, None, None, None, None, None, None, None, None, None, None, None, None, None],
    [None, '#f4731e', '#722a01', None, None, '#f4731f', None, '#f5731f', None, '#f4731f', None, None, '#f4721e', None, '#f4731f', None, '#f4731f', None, None, None, '#732a01', None, None, None, None, None, None, None, None, None, None, None],
    [None, '#f4731e', '#f4721e', None, None, '#f5731e', None, '#f5731f', None, '#f5721e', None, None, '#f4731e', None, '#f4731e', None, '#732b00', '#f5731f', None, '#722a00', '#732b00', '#722b00', None, '#202021', '#202021', None, '#202121', '#202020', None, '#212120', '#202120', None],
    [None, '#f5731f', None, None, None, '#f5731e', '#f5731e', '#732a01', None, '#f5731e', '#f5721f', None, '#f5721f', '#f4731e', '#722a00', None, '#f5721e', '#f4731e', None, None, '#722a01', None, None, None, None, None, None, None, None, None, None, None],
]

REST_1_HEADER = [
    [None, '#f5731e', '#f4721f', None, None, '#f5731e', '#f4731f', '#f5731e', None, '#f5721e', '#f5731f', None, '#f4731f', '#f5731e', '#f4731f', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
    [None, '#f5731e', '#722b00', '#f5721e', None, '#f5721f', '#f5731f', '#732b00', None, '#f5721e', None, None, None, '#f4731f', None, None, None, None, None, None, None, None, None, '#732b00', None, None, None, None, None, None, None, None],
    [None, '#f4721f', '#f4731e', '#732b00', None, '#f4731e', '#732a01', None, None, '#732b01', '#f4721f', None, None, '#f5721e', None, None, None, None, None, '#722b00', '#722a00', None, '#722b00', '#732a01', '#732a00', None, '#212021', '#202120', None, '#202120', '#212021', None],
    [None, '#f4731f', None, '#f4721f', None, '#f5731e', '#f5731e', '#f5731e', None, '#f5721e', '#f4731e', None, None, '#f5721e', None, None, None, None, None, None, None, None, None, '#722b01', None, None, None, None, None, None, None, None],
]

FOCUS_2_HEADER = [
    [None, '#f4721f', '#f4721f', '#f4731f', None, None, '#f5721f', '#f4731f', None, '#f5721e', '#f4731e', None, '#f4731e', None, '#f5731f', None, '#f4731f', '#f4731e', None, None, None, None, None, None, None, None, None, None, None, None, None, None],
    [None, '#f4721f', '#722b01', None, None, '#f4731f', None, '#f5731f', None, '#f4731e', None, None, '#f5721e', None, '#f5721f', None, '#f5721f', None, None, None, None, None, None, None, None, None, '#722b00', None, None, None, None, None],
    [None, '#f4731f', '#f4731e', None, None, '#f5721e', None, '#f5721e', None, '#f5731e', None, None, '#f5721e', None, '#f4721f', None, '#732a00', '#f4731e', None, '#722b00', '#722a00', None, '#722b00', '#722a00', None, '#732b00', '#732b01', '#732b01', None, '#212021', '#202021', None],
    [None, '#f5721f', None, None, None, '#f4721f', '#f5721e', '#722a00', None, '#f5721e', '#f4721f', None, '#f5721f', '#f5721f', '#732a00', None, '#f4731f', '#f5731f', None, None, None, None, None, None, None, None, '#722a01', None, None, None, None, None],
]

REST_2_HEADER = [
    [None, '#f5721e', '#f5721f', None, None, '#f5721f', '#f5731f', '#f4721f', None, '#f5731f', '#f4721e', None, '#f4721f', '#f4731f', '#f4731f', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
    [None, '#f5731f', '#732a01', '#f5731f', None, '#f4731e', '#f5731f', '#732b00', None, '#f5731e', None, None, None, '#f4731f', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, '#732a01', None, None],
    [None, '#f4721f', '#f4731f', '#732a01', None, '#f5721e', '#722a01', None, None, '#722a01', '#f4721f', None, None, '#f5721f', None, None, None, None, None, '#732a00', '#732a00', None, '#722b00', '#722b01', None, '#722b00', '#722b00', None, '#722a00', '#732b00', '#722b01', None],
    [None, '#f5731f', None, '#f4731e', None, '#f5731f', '#f5731f', '#f4731f', None, '#f5721f', '#f4721f', None, None, '#f5721f', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, '#722a00', None, None],
]

SESSION_HEADERS = [FOCUS_1_HEADER, REST_1_HEADER, FOCUS_2_HEADER, REST_2_HEADER]

# <=== {Themeable VFD Color Definitions} ===>
LIT_CORE = "#a5c9ff"           # VFD cyan/ice-blue segment core
LIT_GLOW = "#355283"           # VFD subtle deep blue internal tube glow
UNLIT_CORE = "#252525"         # Dark charcoal filament when unlit
UNLIT_GLOW = "#121212"         # Dark interior background

COLON_LIT = "#a5c9ff"          # Colon dots active
COLON_UNLIT = "#252525"        # Colon dots inactive

INDICATOR_LIT = "#ff5f00"      # Orange indicator cross center
INDICATOR_GLOW = "#722a01"     # Orange indicator glow corners

PROGRESS_ORANGE = "#732a00"    # Darker orange fill color for progress elements
PROGRESS_UNLIT = "#212020"     # Unlit grey for progress elements


# <=== {PomodoroApp} :: {Pomodoro Focus & Rest Cycle with VFD 7-Segment Display} ===>
class PomodoroApp(AppBase):
    _cached_template = None

    def __init__(self, kernel):
        super().__init__()
        self.appName = "Pomodoro"
        self.kernel = kernel

        self.template = self.getTemplate()

        self.sessionIndex = 0           # 0=Focus 1, 1=Rest 1, 2=Focus 2, 3=Rest 2
        self.state = "STOPPED"          # STOPPED, RUNNING, PAUSED, ALARM
        self.selection = "MINUTES"      # MINUTES, SECONDS
        self.minutes = 25
        self.seconds = 0
        self.totalSeconds = (self.minutes * 60) + self.seconds
        self.lastTick = 0.0
        self.lastBlinkState = True
        self.alarmSignaled = False
        self.needsRedraw = True

    @property
    def mode(self) -> str:
        """Returns 'FOCUS' for even sessions (0, 2) and 'REST' for odd sessions (1, 3)."""
        return "FOCUS" if self.sessionIndex % 2 == 0 else "REST"

    @classmethod
    def getTemplate(cls):
        """Loads the 32x32 unlit VFD UI background template."""
        if cls._cached_template is not None:
            return cls._cached_template

        anims_dir = get_anims_dir()
        paths_to_check = [
            os.path.join(anims_dir, "ui-timer-off.png"),
            os.path.join(os.path.dirname(__file__), "..", "anims", "ui-timer-off.png"),
            os.path.join(os.path.dirname(__file__), "..", "..", "gif", "ui-timer-off.png"),
        ]

        for p in paths_to_check:
            if os.path.isfile(p):
                try:
                    img = Image.open(p).convert("RGB")
                    grid = []
                    for y in range(32):
                        row = []
                        for x in range(32):
                            r, g, b = img.getpixel((x, y))
                            row.append(f"#{r:02x}{g:02x}{b:02x}")
                        grid.append(row)
                    cls._cached_template = grid
                    print(f"[PomodoroApp] Loaded VFD background template from {p}")
                    return cls._cached_template
                except Exception as e:
                    print(f"[PomodoroApp] Failed loading template from {p}: {e}")

        # Fallback 32x32 black grid
        cls._cached_template = [["#050505" for _ in range(32)] for _ in range(32)]
        return cls._cached_template

    def onFocus(self):
        self.needsRedraw = True

    def update(self) -> bool:
        now = time.time()
        blink_state = int(now * 2) % 2 == 0  # Toggles every 0.5s

        if self.state == "RUNNING":
            if now - self.lastTick >= 1.0:
                self.lastTick = now
                self.tick()
                self.needsRedraw = True
                return True

            if self.lastBlinkState != blink_state:
                self.lastBlinkState = blink_state
                self.needsRedraw = True
                return True

        elif self.state in ("STOPPED", "PAUSED", "ALARM"):
            if self.lastBlinkState != blink_state:
                self.lastBlinkState = blink_state
                self.needsRedraw = True
                return True

        if self.needsRedraw:
            self.needsRedraw = False
            return True

        return False

    def tick(self):
        if self.seconds > 0:
            self.seconds -= 1
        elif self.minutes > 0:
            self.minutes -= 1
            self.seconds = 59
        else:
            self.state = "ALARM"
            self.alarmSignaled = False

    def render(self, gridManager):
        now = time.time()
        blink_on = int(now * 2) % 2 == 0

        # 1. Base VFD background template
        for y in range(32):
            for x in range(32):
                gridManager.setPixel(x, y, self.template[y][x])

        # 2. Header (Title + 4 Session Indicators: 32x4)
        header_matrix = SESSION_HEADERS[self.sessionIndex]
        for ty in range(4):
            for tx in range(32):
                c = header_matrix[ty][tx]
                gridManager.setPixel(tx, ty, c if c is not None else "#000000")

        # 4. Render 4 VFD Digits (MM:SS) with Core & Inner Tube Glow
        digits_str = f"{self.minutes:02d}{self.seconds:02d}"

        for i, ch in enumerate(digits_str):
            sx, sy = SLOT_COORDS[i]
            is_selected = (self.selection == "MINUTES" and i in (0, 1)) or (self.selection == "SECONDS" and i in (2, 3))

            # Blink logic for selected digits during pause/stopped, or all digits during alarm
            if (self.state in ("STOPPED", "PAUSED") and is_selected and not blink_on) or (self.state == "ALARM" and not blink_on):
                continue

            active_segs = DIGITS.get(ch, "")

            # First pass: Draw inner tube glow around active segments
            for seg_name in active_segs:
                for gx, gy in SEGMENTS[seg_name]["glow"]:
                    px, py = sx + gx, sy + gy
                    if 0 <= px < 32 and 0 <= py < 32:
                        gridManager.setPixel(px, py, LIT_GLOW)

            # Second pass: Draw crisp lit core filaments
            for seg_name in active_segs:
                for cx, cy in SEGMENTS[seg_name]["core"]:
                    px, py = sx + cx, sy + cy
                    if 0 <= px < 32 and 0 <= py < 32:
                        gridManager.setPixel(px, py, LIT_CORE)

        # 5. Colon Dots (blinks 0.5s each second when running or alarm)
        colon_active = (self.state == "RUNNING" and blink_on) or (self.state == "ALARM" and blink_on)
        if colon_active:
            for cx, cy in COLON_DOTS:
                gridManager.setPixel(cx, cy, COLON_LIT)
                gridManager.setPixel(cx + 1, cy, COLON_LIT)
                gridManager.setPixel(cx, cy + 1, COLON_LIT)
                gridManager.setPixel(cx + 1, cy + 1, COLON_LIT)

        # 6. Orange Indicator:
        # - When running: blinks with 0.5s lit / 0.5s unlit
        # - When paused / stopped: completely blacked out (not visible)
        ix, iy = ORANGE_INDICATOR
        if self.state == "RUNNING" and blink_on:
            # Lit cross center and arms
            gridManager.setPixel(ix + 1, iy + 1, INDICATOR_LIT)
            gridManager.setPixel(ix + 1, iy, INDICATOR_LIT)
            gridManager.setPixel(ix, iy + 1, INDICATOR_LIT)
            gridManager.setPixel(ix + 2, iy + 1, INDICATOR_LIT)
            gridManager.setPixel(ix + 1, iy + 2, INDICATOR_LIT)
            # Corner glow
            gridManager.setPixel(ix, iy, INDICATOR_GLOW)
            gridManager.setPixel(ix + 2, iy, INDICATOR_GLOW)
            gridManager.setPixel(ix, iy + 2, INDICATOR_GLOW)
            gridManager.setPixel(ix + 2, iy + 2, INDICATOR_GLOW)
        else:
            # Completely blacked out on pause / stopped screen
            for dy in range(3):
                for dx in range(3):
                    gridManager.setPixel(ix + dx, iy + dy, "#000000")

        # 7. Bottom Progress Bar:
        # Fills from left with darker orange color as timer counts down.
        # Greyed out on pause / stopped screens.
        current_seconds = (self.minutes * 60) + self.seconds
        total_sec = max(1, self.totalSeconds)

        if self.state == "ALARM":
            progress = 1.0
        elif self.state == "RUNNING":
            progress = min(1.0, max(0.0, (total_sec - current_seconds) / total_sec))
        else:
            progress = 0.0

        if self.state in ("RUNNING", "ALARM"):
            num_filled = int(progress * len(PROGRESS_PIXELS))
            if progress >= 1.0:
                num_filled = len(PROGRESS_PIXELS)

            for idx, (px, py) in enumerate(PROGRESS_PIXELS):
                color = PROGRESS_ORANGE if idx < num_filled else PROGRESS_UNLIT
                gridManager.setPixel(px, py, color)
        else:
            # Greyed out on pause / stopped screens
            for px, py in PROGRESS_PIXELS:
                gridManager.setPixel(px, py, PROGRESS_UNLIT)

    def onInput(self, key: str):
        if key in ("Left", "Right"):
            if self.state in ("STOPPED", "PAUSED"):
                self.selection = "SECONDS" if self.selection == "MINUTES" else "MINUTES"
                self.needsRedraw = True

        elif key == "Up":
            if self.state in ("STOPPED", "PAUSED"):
                if self.selection == "MINUTES":
                    self.minutes = (self.minutes + 1) % 100
                elif self.selection == "SECONDS":
                    if self.seconds >= 45:
                        self.seconds = 0
                    else:
                        self.seconds = self.seconds + 15
                # Reset total duration when timer is edited so progress bar restarts from beginning
                self.totalSeconds = (self.minutes * 60) + self.seconds
                self.needsRedraw = True

        elif key == "Down":
            if self.state in ("STOPPED", "PAUSED"):
                if self.selection == "MINUTES":
                    self.minutes = (self.minutes - 1) % 100
                elif self.selection == "SECONDS":
                    if self.seconds <= 15:
                        self.seconds = 0
                    else:
                        self.seconds = self.seconds - 15
                # Reset total duration when timer is edited so progress bar restarts from beginning
                self.totalSeconds = (self.minutes * 60) + self.seconds
                self.needsRedraw = True

        elif key == "Enter":
            if self.state in ("STOPPED", "PAUSED"):
                if self.minutes == 0 and self.seconds == 0:
                    return
                if self.state == "STOPPED":
                    self.totalSeconds = (self.minutes * 60) + self.seconds
                self.state = "RUNNING"
                self.lastTick = time.time()
                self.alarmSignaled = False
            elif self.state == "RUNNING":
                self.state = "PAUSED"
            elif self.state == "ALARM":
                # Advance to next session in Pomodoro cycle: Focus (25m) <-> Rest (5m)
                self.sessionIndex = (self.sessionIndex + 1) % 4
                self.state = "STOPPED"
                self.minutes = 25 if self.mode == "FOCUS" else 5
                self.seconds = 0
                self.totalSeconds = (self.minutes * 60) + self.seconds
                self.selection = "MINUTES"
                self.alarmSignaled = False
            self.needsRedraw = True
