from core.appBase import AppBase
from core.gridSystem import GridManager
from core.themes import ThemeManager

# <=== {Kernel} :: {Manages device power state, apps, and input routing} ===>
class OSKernel:
    
    # <=== {Constructor} :: {Initialize grid, themes, and power state} ===>
    def __init__(self, gridManager: GridManager):
        self.grid = gridManager
        self.themeManager = ThemeManager()
        self.apps = {} # map name -> app_instance
        self.currentAppName = None
        self.activeApp = None
        self.isPowered = False
        self.powerStateChanged = False
        self.menuApp = None

    # <=== {RegisterApp} :: {Add an app to the system} ===>
    def registerApp(self, name: str, app: AppBase):
        self.apps[name] = app

    # <=== {PowerControl} :: {Manage device power state} ===>
    def powerOn(self):
        self.isPowered = True
        self.powerStateChanged = True
        self.switchApp("Boot")
        print("Device powered ON (Booting)")

    def powerOff(self):
        self.isPowered = False
        self.powerStateChanged = True
        self.activeApp = None
        self.currentAppName = None
        self.grid.clearGrid("#000000")
        print("Device powered OFF")

    def togglePower(self):
        if self.isPowered:
            self.powerOff()
        else:
            self.powerOn()

    # <=== {SwitchApp} :: {Change current active app} ===>
    def switchApp(self, name: str):
        if not self.isPowered and name != "Boot":
            return
        if name in self.apps:
            self.currentAppName = name
            self.activeApp = self.apps[name]
            self.activeApp.onFocus() # <--- Trigger refresh
            print(f"Switched to app: {name}")
            # Clear with theme background
            self.grid.clearGrid(self.themeManager.get().background)

    # <=== {HandleInput} :: {Route input to app or handle power/global keys} ===>
    def handleInput(self, key: str):
        # When device is powered OFF: only allow Boot / Power actions to turn on
        if not self.isPowered:
            if key in ("Boot", "Power", "PowerOn", "PowerToggle"):
                self.powerOn()
            return

        # When device is powered ON:
        if key in ("Power", "PowerOff", "PowerToggle"):
            self.powerOff()
            return

        # Global Menu Key
        if key == "Menu":
            self.switchApp("Menu")
            return

        # Global Boot Key (reboots / restarts boot sequence)
        if key == "Boot":
            self.switchApp("Boot")
            return

        if self.activeApp:
            self.activeApp.onInput(key)

    # <=== {Update} :: {Run app cycle} ===>
    def update(self) -> bool:
        if self.powerStateChanged:
            self.powerStateChanged = False
            return True

        if self.isPowered and self.activeApp:
            # Let active app update logic
            logicChanged = self.activeApp.update()
            
            # If logic changed, redraw app to grid
            if logicChanged:
                self.grid.clearGrid(self.themeManager.get().background)
                self.activeApp.render(self.grid)
                return True
        return False
