from core.appBase import AppBase
import random

# <=== {SnakeApp} :: {Classic Snake Game} ===>
class SnakeApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Snake"
        self.kernel = kernel
        self.reset()

    def reset(self):
        self.snake = [(8, 8), (8, 9), (8, 10)] # Head at index 0
        self.direction = (0, -1) # Moving Up
        self.apple = self.spawnApple()
        self.state = "ALIVE"
        self.needsRedraw = True
        
        # Slower speed for snake
        self.moveDelay = 0.15
        self.lastMove = 0

    def spawnApple(self):
        while True:
            x = random.randint(0, 15)
            y = random.randint(0, 15)
            if (x, y) not in self.snake:
                return (x, y)

    def update(self) -> bool:
        if self.state == "GAMEOVER": return False

        import time
        now = time.time()
        if now - self.lastMove < self.moveDelay:
            return False
            
        self.lastMove = now
        
        # Move Head
        headX, headY = self.snake[0]
        dx, dy = self.direction
        newHead = (headX + dx, headY + dy)
        
        # Collision Check
        if (newHead[0] < 0 or newHead[0] >= 16 or 
            newHead[1] < 0 or newHead[1] >= 16 or 
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
            self.moveDelay = max(0.1, self.moveDelay * 0.98)
        else:
            self.snake.pop() # Remove tail
            
        self.needsRedraw = True
        return True

    def render(self, gridManager):
        # Draw Apple
        ax, ay = self.apple
        gridManager.setPixel(ax, ay, "#FF0000") # Red Apple
        
        # Draw Snake
        color = "#00FF00" if self.state == "ALIVE" else "#555555" # Gray if dead
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
