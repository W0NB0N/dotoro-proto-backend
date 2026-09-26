from core.appBase import AppBase
from core.graphics import Graphics, FONT_5X7
import random
import time

# <=== {SnakeApp} :: {Classic Snake Game on 32x32 Grid} ===>
class SnakeApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Snake"
        self.kernel = kernel
        self.reset()

    def reset(self):
        # Position snake in center of 32x32 grid
        self.snake = [(16, 16), (16, 17), (16, 18)] # Head at index 0
        self.direction = (0, -1) # Moving Up
        self.apple = self.spawnApple()
        self.state = "ALIVE"
        self.needsRedraw = True
        
        # Adjust move speed (150ms per tick)
        self.moveDelay = 0.15
        self.lastMove = 0

    def spawnApple(self):
        while True:
            # Random position within 32x32 bounds
            x = random.randint(0, 31)
            y = random.randint(0, 31)
            if (x, y) not in self.snake:
                return (x, y)

    def update(self) -> bool:
        if self.state == "GAMEOVER": return False

        now = time.time()
        if now - self.lastMove < self.moveDelay:
            return False
            
        self.lastMove = now
        
        # Move Head
        headX, headY = self.snake[0]
        dx, dy = self.direction
        newHead = (headX + dx, headY + dy)
        
        # Collision Check (32x32 bounds)
        if (newHead[0] < 0 or newHead[0] >= 32 or 
            newHead[1] < 0 or newHead[1] >= 32 or 
            newHead in self.snake[:-1]):
            self.state = "GAMEOVER"
            self.needsRedraw = True
            return True

        # Move Logic
        self.snake.insert(0, newHead)
        
        # Eat Apple
        if newHead == self.apple:
            self.apple = self.spawnApple()
            # Speed up slightly
            self.moveDelay = max(0.08, self.moveDelay * 0.98)
        else:
            self.snake.pop() # Remove tail
            
        self.needsRedraw = True
        return True

    def render(self, gridManager):
        theme = self.kernel.themeManager.get()
        
        if self.state == "GAMEOVER":
            gridManager.clearGrid(theme.background)
            # Draw GAME OVER centered in FONT_5X7
            Graphics.drawTextCentered(gridManager, 6, "GAME", theme.danger, FONT_5X7)
            Graphics.drawTextCentered(gridManager, 16, "OVER", theme.danger, FONT_5X7)
            
            # Press enter hint at bottom in FONT_3X5 (Wait, we can import FONT_3X5 fallback or just write standard)
            # "ENTER TO RESTART" - wait, let's write "ENTER" at y=26 in 3x5 font!
            from core.graphics import FONT_3X5
            Graphics.drawTextCentered(gridManager, 26, "ENTER TO PLAY", theme.secondary, FONT_3X5)
            return

        # Draw Apple
        ax, ay = self.apple
        gridManager.setPixel(ax, ay, theme.appleColor)
        
        # Draw Snake
        color = theme.snakeColor
        for sx, sy in self.snake:
            gridManager.setPixel(sx, sy, color)

    def onInput(self, key: str):
        if self.state == "GAMEOVER" and key == "Enter":
            self.reset()
            return

        newDir = None
        if key == "Up": newDir = (0, -1)
        if key == "Down": newDir = (0, 1)
        if key == "Left": newDir = (-1, 0)
        if key == "Right": newDir = (1, 0)
        
        if newDir:
            # Prevent 180 turn
            cx, cy = self.direction
            if newDir[0] != -cx and newDir[1] != -cy:
                self.direction = newDir
