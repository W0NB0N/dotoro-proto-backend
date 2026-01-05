from dataclasses import dataclass, asdict

# <=== {Theme} :: {Color palette definition} ===>
@dataclass
class Theme:
    name: str
    # Core
    background: str
    foreground: str
    accent: str
    secondary: str
    
    # Semantic
    success: str
    warning: str
    danger: str
    
    # Game Overrides
    snakeColor: str
    appleColor: str
    
    # Ambient (Frontend)
    ambientBg: str
    ambientAccent: str
    ambientGif: str
    screenGlow: str

# <=== {Presets} :: {Predefined themes} ===>
CYBERPUNK = Theme(
    name="cyberpunk",
    background="#120458", foreground="#00f0ff", accent="#ff0099", secondary="#7000ff",
    success="#00ff9f", warning="#ffbf00", danger="#ff0000",
    snakeColor="#00ff9f", appleColor="#ff0000",
    ambientBg="#0a0220", ambientAccent="#ff0099", ambientGif="cyberpunk_city", screenGlow="#ff0099"
)

FOREST = Theme(
    name="forest",
    background="#0c1a11", foreground="#d1e8d6", accent="#4caf50", secondary="#2e7d32",
    success="#aeea00", warning="#ffc107", danger="#e53935",
    snakeColor="#8bc34a", appleColor="#ff5722",
    ambientBg="#050e06", ambientAccent="#4caf50", ambientGif="forest_rain", screenGlow="#8bc34a"
)

RETROWAVE = Theme(
    name="retrowave",
    background="#241734", foreground="#fdfdfd", accent="#ff71ce", secondary="#01cdfe",
    success="#05ffa1", warning="#b967ff", danger="#ff0000",
    snakeColor="#05ffa1", appleColor="#ff71ce",
    ambientBg="#12001f", ambientAccent="#ff71ce", ambientGif="synthwave_grid", screenGlow="#01cdfe"
)

MINIMAL = Theme(
    name="minimal",
    background="#111111", foreground="#eeeeee", accent="#888888", secondary="#444444",
    success="#ffffff", warning="#cccccc", danger="#555555",
    snakeColor="#ffffff", appleColor="#888888",
    ambientBg="#000000", ambientAccent="#ffffff", ambientGif="minimal_noise", screenGlow="#ffffff"
)

OCEAN = Theme(
    name="ocean",
    background="#001e36", foreground="#d4f1f9", accent="#00b4d8", secondary="#0077b6",
    success="#48cae4", warning="#90e0ef", danger="#03045e",
    snakeColor="#48cae4", appleColor="#ade8f4",
    ambientBg="#001220", ambientAccent="#00b4d8", ambientGif="underwater", screenGlow="#00b4d8"
)

CATPPUCCIN = Theme(
    name="catppuccin",
    background="#1e1e2e", foreground="#cdd6f4", accent="#89b4fa", secondary="#cba6f7",
    success="#a6e3a1", warning="#f9e2af", danger="#f38ba8",
    snakeColor="#a6e3a1", appleColor="#f38ba8",
    ambientBg="#181825", ambientAccent="#89b4fa", ambientGif="mocha_mountains", screenGlow="#89b4fa"
)

THEMES = {
    "cyberpunk": CYBERPUNK,
    "forest": FOREST,
    "retrowave": RETROWAVE,
    "minimal": MINIMAL,
    "ocean": OCEAN,
    "catppuccin": CATPPUCCIN
}

# <=== {ThemeManager} :: {Manage switching} ===>
class ThemeManager:
    def __init__(self):
        self.currentTheme = CYBERPUNK
    
    def setTheme(self, themeName: str):
        if themeName in THEMES:
            self.currentTheme = THEMES[themeName]
            print(f"Theme switched to: {themeName}")
            
    def get(self) -> Theme:
        return self.currentTheme

    def listThemes(self) -> list[str]:
        return list(THEMES.keys())

    def toClientPayload(self) -> dict:
        return asdict(self.currentTheme)
