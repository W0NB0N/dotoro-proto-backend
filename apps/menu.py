import time
from core.appBase import AppBase
from core.graphics import Graphics, FONT_5X7

# <=== {MenuApp} :: {App Selection Screen on 32x32 grid} ===>
class MenuApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Menu"
        self.kernel = kernel
        self.options = ["Pomodoro", "Snake", "Theme", "Gallery"]
        self.maxIndex = len(self.options) - 1
        self.currentIndex = 0
        
        self.font = FONT_5X7
        self.needsRedraw = True

    def onFocus(self):
        self.needsRedraw = True

    def getTextWidth(self, text: str) -> int:
        totalWidth = 0
        for char in text:
            charKey = char.upper()
            bitmap = self.font.get(charKey, self.font.get(' ', [[0]]))
            totalWidth += len(bitmap[0]) + 1
        if totalWidth > 0:
            totalWidth -= 1
        return totalWidth

    # <=== {Update} :: {Handle animation and redraw logic} ===>
    def update(self) -> bool:
        currentText = self.options[self.currentIndex].upper()
        if currentText != "POMODORO":
            textWidth = self.getTextWidth(currentText)
            # If it overflows 32px, we return True to update the marquee animation continuously
            if textWidth > 32:
                return True
            
        if self.needsRedraw:
            self.needsRedraw = False
            return True
            
        return False

    # <=== {Render} :: {Draw menu options and pagination dots} ===>
    def render(self, gridManager):
        theme = self.kernel.themeManager.get()
        selected = self.options[self.currentIndex]
        
        # Determine color based on selection
        color = theme.accent
        if self.currentIndex == 2:
            color = theme.warning
        elif self.currentIndex == 3:
            color = theme.success
            
        # Draw Pomodoro as 2 stacked lines: "POMO" then "DORO"
        if selected == "Pomodoro":
            Graphics.drawTextCentered(gridManager, 7, "POMO", color, self.font)
            Graphics.drawTextCentered(gridManager, 15, "DORO", color, self.font)
        else:
            # Single centered marquee line for other apps at y=12
            Graphics.drawMarqueeText(gridManager, 0, 12, 32, selected.upper(), color, int(time.time() * 1000), 12.0, self.font)
            
        # Draw Dots for pagination (balanced for 32x32)
        # Dot width = 3, height = 2, spacing = 2
        dotWidth = 3
        dotHeight = 2
        spacing = 2
        totalDotWidth = len(self.options) * (dotWidth + spacing) - spacing
        startX = (32 - totalDotWidth) // 2
        dotY = 26

        for i in range(len(self.options)):
            c = theme.foreground if i == self.currentIndex else theme.secondary
            Graphics.drawRect(gridManager, startX + i * (dotWidth + spacing), dotY, dotWidth, dotHeight, c, True)

    # <=== {Input} :: {Navigate menu options} ===>
    def onInput(self, key: str):
        if key == "Left":
            self.currentIndex = max(0, self.currentIndex - 1)
            self.needsRedraw = True
        elif key == "Right":
            self.currentIndex = min(self.maxIndex, self.currentIndex + 1)
            self.needsRedraw = True
        elif key == "Enter":
            selected = self.options[self.currentIndex]
            if selected == "Theme":
                self.kernel.switchApp("Themes")
            else:
                self.kernel.switchApp(selected)
