import random
import time
from core.appBase import AppBase
from core.graphics import Graphics, FONT_3X5

# <=== {Theme & Visual Constants} ===>
BG_COLOR = "#9dbf4e"   # Classic Game Boy green background
FG_COLOR = "#322f3b"   # Dark slate foreground for snake, apples, border & text

# 10-cell closed perimeter loop for the length-9 snake animation on start / game over screen
# Cell coordinates (x, y) moving clockwise in a 4x3 rectangle
LOOP_PATH = [
    (14, 13), (15, 13), (16, 13), (17, 13),
    (17, 14),
    (17, 15), (16, 15), (15, 15), (14, 15),
    (14, 14)
]

# Inner playable area bounds inside the 30x26 border box
# Outer border: x=1..30, y=5..30 (1px margins at left x=0, right x=31, bottom y=31; top y=0..4 for score)
MIN_PLAY_X = 2
MAX_PLAY_X = 29
MIN_PLAY_Y = 6
MAX_PLAY_Y = 29


class SnakeApp(AppBase):
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Snake"
        self.kernel = kernel

        self.highScore = 0
        self.score = 0
        self.lastScore = 0

        # Animation state for loop
        self.animFrame = 0
        self.lastAnimTick = 0

        # Start in START screen
        self.state = "START"
        self.resetGameData()

    def resetGameData(self):
        """Initializes gameplay variables for a new run."""
        # Snake in center of inner playfield, moving UP
        self.snake = [(15, 16), (15, 17), (15, 18)]
        self.direction = (0, -1)
        self.inputQueue = []

        self.score = 0
        self.apples = []
        self.spawnApples(count=self.getTargetAppleCount())

        self.moveDelay = 0.16
        self.lastMove = 0
        self.gameStartTime = time.time()
        self.needsRedraw = True

    def getTargetAppleCount(self) -> int:
        """Determines maximum simultaneous apples; decreases as score increases."""
        if self.score < 5:
            return 4
        elif self.score < 12:
            return 3
        elif self.score < 25:
            return 2
        else:
            return 1

    def spawnApples(self, count=1):
        """Spawns up to `count` apples at once within playfield bounds without overlapping snake or existing apples."""
        target = self.getTargetAppleCount()
        needed = min(count, max(1, target - len(self.apples)))

        for _ in range(needed):
            if len(self.apples) >= target:
                break
            cell = self.getFreeCell()
            if cell:
                self.apples.append(cell)

    def getFreeCell(self):
        """Finds a random unoccupied cell inside the inner playable area."""
        occupied = set(self.snake) | set(self.apples)
        available = [
            (x, y)
            for x in range(MIN_PLAY_X, MAX_PLAY_X + 1)
            for y in range(MIN_PLAY_Y, MAX_PLAY_Y + 1)
            if (x, y) not in occupied
        ]
        if available:
            return random.choice(available)
        return None

    def startGame(self):
        """Transitions to ALIVE state and begins a round."""
        self.resetGameData()
        self.state = "ALIVE"
        self.needsRedraw = True

    def update(self) -> bool:
        now = time.time()

        # Update snake loop animation during START and GAMEOVER screens
        if self.state in ("START", "GAMEOVER"):
            if now - self.lastAnimTick >= 0.12:
                self.lastAnimTick = now
                self.animFrame = (self.animFrame + 1) % 10
                self.needsRedraw = True
                return True
            return False

        # ALIVE state: snake movement and speed scaling
        elapsed = now - self.gameStartTime
        # Speed increases with time survived and apples eaten
        current_delay = max(0.06, 0.16 - (elapsed * 0.0006) - (self.score * 0.002))

        if now - self.lastMove < current_delay:
            return False

        self.lastMove = now

        # Consume 1 queued directional input per tick
        if self.inputQueue:
            self.direction = self.inputQueue.pop(0)

        # Move head
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Collision with 1px border perimeter
        if (
            new_head[0] < MIN_PLAY_X
            or new_head[0] > MAX_PLAY_X
            or new_head[1] < MIN_PLAY_Y
            or new_head[1] > MAX_PLAY_Y
            or new_head in self.snake[:-1]
        ):
            self.state = "GAMEOVER"
            self.lastScore = self.score
            self.highScore = max(self.highScore, self.score)
            self.needsRedraw = True
            return True

        # Advance snake
        self.snake.insert(0, new_head)

        # Check apple consumption
        if new_head in self.apples:
            self.apples.remove(new_head)
            self.score += 1
            self.highScore = max(self.highScore, self.score)

            # Spawn more than 1 apple at once early on; rate decreases as game progresses
            spawn_count = 2 if self.score < 8 else 1
            self.spawnApples(count=spawn_count)
        else:
            self.snake.pop()  # Remove tail segment

        self.needsRedraw = True
        return True

    def render(self, gridManager):
        now = time.time()
        # 1. Background fill
        gridManager.clearGrid(BG_COLOR)

        # 2. Draw 1px border around the 30x26 area
        # Box from x=1 to x=30, y=5 to y=30 (1px space at left x=0, right x=31, bottom y=31)
        Graphics.drawRect(gridManager, 1, 5, 30, 26, FG_COLOR)

        # 3. Render state-specific content
        if self.state in ("START", "GAMEOVER"):
            # Header text ("SNAKE" on start, "OVER" on game over)
            title = "SNAKE" if self.state == "START" else "OVER"
            Graphics.drawTextCentered(gridManager, 7, title, FG_COLOR, FONT_3X5)

            # Snake of length 9 following its own tail in a continuous loop
            loop_segs = [LOOP_PATH[(self.animFrame - i) % 10] for i in range(9)]
            for lx, ly in loop_segs:
                gridManager.setPixel(lx, ly, FG_COLOR)

            # Score display:
            # - Start Screen: Highest score ("HI <highScore>")
            # - Game Over Screen: Last score with highest score ("<score> HI <highScore>")
            if self.state == "START":
                Graphics.drawTextCentered(gridManager, 18, f"HI {self.highScore}", FG_COLOR, FONT_3X5)
            else:
                # Top counter also displays final score
                Graphics.drawTextCentered(gridManager, 0, str(self.score), FG_COLOR, FONT_3X5)

                score_str = f"{self.score} HI {self.highScore}"
                # If fits on one line within 28px inner area, draw centered; otherwise alternate
                width = sum(len(FONT_3X5.get(c.upper(), [[0]])[0]) + 1 for c in score_str) - 1
                if width <= 27:
                    Graphics.drawTextCentered(gridManager, 18, score_str, FG_COLOR, FONT_3X5)
                else:
                    # Alternating score display if numbers are very large
                    alt = f"SC {self.score}" if int(now * 0.8) % 2 == 0 else f"HI {self.highScore}"
                    Graphics.drawTextCentered(gridManager, 18, alt, FG_COLOR, FONT_3X5)

            # Blinking "ENTER" prompt at bottom of inner area
            if int(now * 2) % 2 == 0:
                Graphics.drawTextCentered(gridManager, 24, "ENTER", FG_COLOR, FONT_3X5)

        elif self.state == "ALIVE":
            # Simple score counter on top outside the border (y=0..4) in 3x5 font
            Graphics.drawTextCentered(gridManager, 0, str(self.score), FG_COLOR, FONT_3X5)

            # Draw Apples
            for ax, ay in self.apples:
                gridManager.setPixel(ax, ay, FG_COLOR)

            # Draw Snake
            for sx, sy in self.snake:
                gridManager.setPixel(sx, sy, FG_COLOR)

    def onInput(self, key: str):
        if self.state in ("START", "GAMEOVER"):
            if key in ("Enter", "Space", "Up", "Down", "Left", "Right"):
                self.startGame()
            return

        dir_map = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
        }

        if key in dir_map:
            new_dir = dir_map[key]
            # Determine reference direction: compare against the last queued direction if any,
            # otherwise compare against current moving direction
            ref_dir = self.inputQueue[-1] if self.inputQueue else self.direction

            # Disallow 180° immediate reversal and ignore duplicate inputs
            is_reverse = (new_dir[0] == -ref_dir[0] and new_dir[1] == -ref_dir[1])
            if not is_reverse and new_dir != ref_dir:
                if len(self.inputQueue) < 2:
                    self.inputQueue.append(new_dir)
