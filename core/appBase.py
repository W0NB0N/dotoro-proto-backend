from abc import ABC, abstractmethod

# <=== {AppInterface} :: {Base class for all virtual os apps} ===>
class AppBase(ABC):
    
    # <=== {Constructor} :: {Initialize app state} ===>
    def __init__(self):
        self.appName = "Unknown"
        self.isActive = False

    # <=== {UpdateMethod} :: {Process logic return true if screen needs redraw} ===>
    @abstractmethod
    def update(self) -> bool:
        pass

    # <=== {RenderMethod} :: {Draw app state onto the provided grid manager} ===>
    @abstractmethod
    def render(self, gridManager):
        pass

    # <=== {InputHandler} :: {Handle keyboard events from frontend} ===>
    @abstractmethod
    def onInput(self, key: str):
        pass
