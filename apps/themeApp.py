from core.appBase import AppBase
from core.graphics import Graphics, FONT_5X7, FONT_3X5
from core.themes import THEMES

# <=== {ThemeApp} :: {Theme Selection Screen on 32x32 Grid} ===>
class ThemeApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Themes"
        self.kernel = kernel
        self.themeNames = self.kernel.themeManager.listThemes()
        self.maxIndex = len(self.themeNames) - 1
        current = self.kernel.themeManager.get().name
        self.currentIndex = self.themeNames.index(current) if current in self.themeNames else 0
        self.needsRedraw = True

    def onFocus(self):
        # Sync index with current theme if possible
        current = self.kernel.themeManager.get().name
        if current in self.themeNames:
            self.currentIndex = self.themeNames.index(current)
        self.needsRedraw = True

    def update(self) -> bool:
        if self.needsRedraw:
            self.needsRedraw = False
            return True
        return False

    def render(self, gridManager):
        # We render the CURRENT selection using ITS OWN theme colors
        # so the user can preview it.
        themeName = self.themeNames[self.currentIndex]
        previewTheme = THEMES[themeName]
        
        # Clear grid with preview background
        gridManager.clearGrid(previewTheme.background)
        
        # Truncate text to fit 32px wide in FONT_5X7
        displayText = Graphics.truncateText(themeName.upper(), 32, FONT_5X7)
        
        # Draw centered theme name
        Graphics.drawTextCentered(gridManager, 13, displayText, previewTheme.accent, FONT_5X7)
        
        # Draw Label "THEME" (top)
        Graphics.drawTextCentered(gridManager, 4, "THEME", previewTheme.secondary, FONT_3X5)

        # Draw Pagination dots (centered, balanced for 32x32)
        dotWidth = 2
        dotHeight = 2
        spacing = 2
        totalDotWidth = len(self.themeNames) * (dotWidth + spacing) - spacing
        startX = (32 - totalDotWidth) // 2
        dotY = 26

        for i in range(len(self.themeNames)):
            c = previewTheme.foreground if i == self.currentIndex else previewTheme.secondary
            Graphics.drawRect(gridManager, startX + i * (dotWidth + spacing), dotY, dotWidth, dotHeight, c, True)

    def onInput(self, key: str):
        if key == "Left":
            self.currentIndex = max(0, self.currentIndex - 1)
            self.needsRedraw = True
        elif key == "Right":
            self.currentIndex = min(self.maxIndex, self.currentIndex + 1)
            self.needsRedraw = True
        elif key == "Enter":
            # Apply Theme
            selectedName = self.themeNames[self.currentIndex]
            self.kernel.themeManager.setTheme(selectedName)
            # Return to Menu
            self.kernel.switchApp("Menu")
