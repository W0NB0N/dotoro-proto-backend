from core.appBase import AppBase
from core.graphics import Graphics
import time

# <=== {TimerApp} :: {Pomodoro Timer Logic} ===>
class TimerApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Timer"
        self.kernel = kernel
        
        self.state = "STOPPED" # STOPPED, RUNNING, ALARM
        self.defaultTime = 25
        self.minutes = self.defaultTime
        self.seconds = 0
        self.totalSeconds = 0
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
        # Background Logic handled by GridManager
        theme = self.kernel.themeManager.get()
        color = theme.foreground
        
        if self.state == "RUNNING": color = theme.accent
        if self.state == "ALARM": color = theme.danger

        # Draw Time "MM:SS" -> "MM" top "SS" bottom
        minStr = f"{self.minutes:02}"
        secStr = f"{self.seconds:02}"
        
        # Center the numbers
        Graphics.drawTextCentered(gridManager, 2, minStr, color)
        
        # Separator (Colon)
        Graphics.drawRect(gridManager, 7, 7, 2, 2, theme.secondary, True)
        
        Graphics.drawTextCentered(gridManager, 10, secStr, color)
        
        # Progress Bar (Only when running)
        if self.state == "RUNNING":
            currentSeconds = (self.minutes * 60) + self.seconds
            if self.totalSeconds > 0:
                progress = currentSeconds / self.totalSeconds
                Graphics.drawProgressBar(gridManager, 0, 15, 16, progress, color, theme.secondary)

    def onFocus(self):
        self.needsRedraw = True

    def onInput(self, key: str):
        if key == "Enter":
            if self.state == "STOPPED" or self.state == "PAUSED":
                if self.state == "STOPPED":
                    self.totalSeconds = (self.minutes * 60) + self.seconds
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
