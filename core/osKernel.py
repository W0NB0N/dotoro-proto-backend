from core.appBase import AppBase
from core.gridSystem import GridManager

# <=== {Kernel} :: {Manages apps and inputs} ===>
class OSKernel:
    
    # <=== {Constructor} :: {Initialize grid and default app} ===>
    def __init__(self, gridManager: GridManager):
        self.grid = gridManager
        self.apps = {} # map name -> app_instance
        self.currentAppName = None
        self.activeApp = None
        
        # We will register apps later
        self.menuApp = None 

    # <=== {RegisterApp} :: {Add an app to the system} ===>
    def registerApp(self, name: str, app: AppBase):
        self.apps[name] = app

    # <=== {SwitchApp} :: {Change current active app} ===>
    def switchApp(self, name: str):
        if name in self.apps:
            self.currentAppName = name
            self.activeApp = self.apps[name]
            print(f"Switched to app: {name}")
            self.grid.clearGrid()

    # <=== {HandleInput} :: {Route input to app or handle global keys} ===>
    def handleInput(self, key: str):
        # Global Menu Key
        if key == "Menu":
            self.switchApp("Menu")
            return

        if self.activeApp:
            self.activeApp.onInput(key)

    # <=== {Update} :: {Run app cycle} ===>
    def update(self) -> bool:
        if self.activeApp:
            # Let app update logic
            logicChanged = self.activeApp.update()
            
            # If logic changed, redraw app to grid
            if logicChanged:
                self.grid.clearGrid()
                self.activeApp.render(self.grid)
                return True
        return False
