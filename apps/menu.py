from core.appBase import AppBase
from core.utils import drawText

# <=== {MenuApp} :: {App Selection Screen} ===>
class MenuApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Menu"
        self.kernel = kernel
        self.options = ["Timer", "Snake"]
        self.maxIndex = len(self.options) - 1
        self.currentIndex = 0
        self.colors = ["#FFD700", "#00FF00"] # Gold, Green
        
        # Init icons/text
        self.needsRedraw = True

    # <=== {Update} :: {Handle logic} ===>
    def update(self) -> bool:
        if self.needsRedraw:
            self.needsRedraw = False
            return True
        return False

    # <=== {Render} :: {Draw menu options} ===>
    def render(self, gridManager):
        # Draw Title "APP"
        # drawText(gridManager, 2, 1, "APP", "#FFFFFF")
        
        # Draw Current Selection
        if self.currentIndex == 0:
            # Timer Icon (T)
            drawText(gridManager, 3, 5, "TIMER", self.colors[0])
        elif self.currentIndex == 1:
            # Snake Icon (S)
            drawText(gridManager, 3, 5, "SNAKE", self.colors[1])
            
        # Draw Dots for pagination
        for i in range(len(self.options)):
            c = "#FFFFFF" if i == self.currentIndex else "#555555"
            gridManager.setPixel(6 + (i*2), 14, c)

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
            self.kernel.switchApp(selected)
