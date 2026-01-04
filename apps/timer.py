from core.appBase import AppBase
from core.utils import drawText
import time

# <=== {TimerApp} :: {Pomodoro Timer Logic} ===>
class TimerApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Timer"
        self.kernel = kernel
        
        self.state = "STOPPED" # STOPPED, RUNNING, ALARM
        self.minutes = 25
        self.seconds = 0
        self.lastTick = 0
        
        self.needsRedraw = True

    def update(self) -> bool:
        now = time.time()
        
        if self.state == "RUNNING":
            if now - self.lastTick >= 1.0:
                self.lastTick = now
                self.tick()
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

    def render(self, gridManager):
        # Background
        color = "#FFFFFF"
        if self.state == "RUNNING": color = "#00FFFF" # Cyan
        if self.state == "ALARM": color = "#FF0000"   # Red

        # Draw Time "MM:SS" is too wide.
        # Draw "MM" top, "SS" bottom
        
        minStr = f"{self.minutes:02}"
        secStr = f"{self.seconds:02}"
        
        drawText(gridManager, 4, 2, minStr, color)
        # Separator
        gridManager.setPixel(7, 7, "#555")
        gridManager.setPixel(8, 7, "#555")
        
        drawText(gridManager, 4, 9, secStr, color)

    def onInput(self, key: str):
        if key == "Enter":
            if self.state == "STOPPED" or self.state == "PAUSED":
                self.state = "RUNNING"
                self.lastTick = time.time()
            elif self.state == "RUNNING":
                self.state = "PAUSED"
            elif self.state == "ALARM":
                self.state = "STOPPED"
                self.minutes = 25
                self.seconds = 0
            self.needsRedraw = True
            
        elif key == "Up" and self.state != "RUNNING":
            self.minutes = min(99, self.minutes + 1)
            self.needsRedraw = True
        elif key == "Down" and self.state != "RUNNING":
            self.minutes = max(1, self.minutes - 1)
            self.needsRedraw = True
