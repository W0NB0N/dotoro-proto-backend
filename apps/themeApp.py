from core.appBase import AppBase
from core.graphics import Graphics
from core.themes import THEMES

# <=== {ThemeApp} :: {Theme Selection Screen} ===>
class ThemeApp(AppBase):
    
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Themes"
        self.kernel = kernel
        self.themeNames = self.kernel.themeManager.listThemes()
        self.maxIndex = len(self.themeNames) - 1
        self.currentIndex = 0
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
        # Temporarily get the preview theme object
        previewTheme = THEMES[themeName]
        
        # Clear grid with preview background
        gridManager.clearGrid(previewTheme.background)
        
        # Truncate text to fit 16px wide
        # "Cyberpunk" -> "Cybe"
        displayText = Graphics.truncateText(themeName, 16)
        
        # Draw centered
        Graphics.drawTextCentered(gridManager, 6, displayText, previewTheme.accent)
        
        # Draw Text Label "THEME" (top)
        Graphics.drawTextCentered(gridManager, 1, "THEME", previewTheme.secondary)

        # Draw Pagination dots
        startX = (16 - (len(self.themeNames) * 2)) // 2
        for i in range(len(self.themeNames)):
            c = previewTheme.foreground if i == self.currentIndex else previewTheme.secondary
            gridManager.setPixel(startX + (i*2), 14, c)

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
