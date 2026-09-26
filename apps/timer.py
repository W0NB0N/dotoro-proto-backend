from core.appBase import AppBase
from core.graphics import Graphics, FONT_5X7, FONT_3X5
import time

# <=== {TimerApp} :: {Pomodoro Timer Logic on 32x32 Grid} ===>
class TimerApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Timer"
        self.kernel = kernel
        
        self.state = "STOPPED" # STOPPED, RUNNING, PAUSED, ALARM
        self.defaultTime = 25
        self.minutes = self.defaultTime
        self.seconds = 0
        self.totalSeconds = 0
        self.lastTick = 0
        
        self.needsRedraw = True
        self.lastBlinkState = True

    def update(self) -> bool:
        now = time.time()
        
        # Blink state switches every 0.5s
        blinkState = int(now * 2) % 2 == 0
        
        if self.state == "RUNNING":
            if now - self.lastTick >= 1.0:
                self.lastTick = now
                self.tick()
                self.needsRedraw = True
                return True
            
            # Trigger redraw on blink state change
            if self.lastBlinkState != blinkState:
                self.lastBlinkState = blinkState
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
        theme = self.kernel.themeManager.get()
        color = theme.foreground
        
        if self.state == "RUNNING": color = theme.accent
        if self.state == "ALARM": color = theme.danger
        elif self.state == "PAUSED": color = theme.secondary

        # 1. Draw Header / Status Label
        headerText = "POMODORO"
        if self.state == "RUNNING":
            headerText = "FOCUS"
        elif self.state == "PAUSED":
            headerText = "PAUSED"
        elif self.state == "ALARM":
            headerText = "ALARM!"
            # Flash background if in alarm
            if int(time.time() * 4) % 2 == 0:
                gridManager.clearGrid(theme.danger)
                # Draw text in white when flashed
                color = "#ffffff"
                
        Graphics.drawTextCentered(gridManager, 2, headerText, theme.secondary, FONT_3X5)

        # 2. Draw Time "MM:SS" on a single line in FONT_5X7
        minStr = f"{self.minutes:02}"
        secStr = f"{self.seconds:02}"
        
        y = 11
        # MM starts at 1
        Graphics.drawText(gridManager, 1, y, minStr, color, FONT_5X7)
        
        # Colon blinks in RUNNING state, static in other states
        now = time.time()
        blinkState = int(now * 2) % 2 == 0
        if self.state != "RUNNING" or blinkState:
            Graphics.drawText(gridManager, 13, y, ":", theme.secondary, FONT_5X7)
            
        # SS starts at 19
        Graphics.drawText(gridManager, 19, y, secStr, color, FONT_5X7)

        # 3. Draw State Icon centered at y=21
        iconY = 21
        if self.state == "RUNNING":
            Graphics.drawIcon(gridManager, 14, iconY, "PLAY", theme.accent)
        elif self.state == "PAUSED":
            Graphics.drawIcon(gridManager, 14, iconY, "PAUSE", theme.secondary)
        elif self.state == "ALARM":
            Graphics.drawIcon(gridManager, 14, iconY, "HEART", theme.danger)
        else:
            Graphics.drawIcon(gridManager, 14, iconY, "CHECK", theme.foreground)

        # 4. Progress Bar at bottom (y=30)
        currentSeconds = (self.minutes * 60) + self.seconds
        if self.state == "RUNNING" or self.state == "PAUSED":
            if self.totalSeconds > 0:
                progress = currentSeconds / self.totalSeconds
                # Progress goes left-to-right (1.0 down to 0.0)
                # Draw the progress bar spanning all 32 pixels
                Graphics.drawProgressBar(gridManager, 0, 30, 32, progress, color, theme.secondary)

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
                self.minutes = self.defaultTime
                self.seconds = 0
            self.needsRedraw = True
            
        elif key == "Up" and self.state != "RUNNING":
            self.minutes = min(99, self.minutes + 1)
            self.needsRedraw = True
        elif key == "Down" and self.state != "RUNNING":
            self.minutes = max(1, self.minutes - 1)
            self.needsRedraw = True
