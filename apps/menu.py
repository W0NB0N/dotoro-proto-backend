from core.appBase import AppBase
from core.graphics import Graphics

# <=== {MenuApp} :: {App Selection Screen} ===>
class MenuApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Menu"
        self.kernel = kernel
        self.options = ["Timer", "Snake", "Theme"]
        self.maxIndex = len(self.options) - 1
        self.currentIndex = 0
        # self.colors = ["#FFD700", "#00FF00"] # Gold, Green (Deprecated)
        
        # Init icons/text
        self.needsRedraw = True

    # <=== {Update} :: {Handle logic} ===>
    def update(self) -> bool:
        if self.needsRedraw:
            self.needsRedraw = False
            return True
        return False

    def onFocus(self):
        self.needsRedraw = True

    # <=== {Render} :: {Draw menu options} ===>
    def render(self, gridManager):
        theme = self.kernel.themeManager.get()
        
        # Draw Current Selection
        if self.currentIndex == 0:
            # Timer Text
            Graphics.drawTextCentered(gridManager, 7, "TIMER", theme.accent)
            # Graphics.drawIcon(gridManager, 2, 6, "ARROW_UP", theme.secondary) # Decoration
        elif self.currentIndex == 1:
            # Snake Text
            Graphics.drawTextCentered(gridManager, 7, "SNAKE", theme.accent)
        elif self.currentIndex == 2:
            # Theme Switcher
            Graphics.drawTextCentered(gridManager, 7, "THEME", theme.warning)
            
        # Draw Dots for pagination
        startX = (16 - (len(self.options) * 3)) // 2 + 1
        for i in range(len(self.options)):
            c = theme.foreground if i == self.currentIndex else theme.secondary
            Graphics.drawRect(gridManager, startX + (i*3), 14, 2, 1, c, True)

    # <=== {Input} :: {Navigate menu} ===>
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
