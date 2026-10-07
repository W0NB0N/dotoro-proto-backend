import os
import time
from core.appBase import AppBase
from core.graphics import Graphics
from core.animLoader import get_anims_dir, load_gif_frames

# <=== {BootApp} :: {Plays dotoro-boot.gif animation on device power on} ===>
class BootApp(AppBase):
    _cached_frames = None

    def __init__(self, kernel):
        super().__init__()
        self.appName = "Boot"
        self.kernel = kernel
        
        self.frames = self.getFrames()
        self.currentFrame = 0
        self.lastFrameTime = 0.0
        self.bootComplete = False
        self.hasSignaledComplete = False
        self.needsRedraw = True

    @classmethod
    def getFrames(cls):
        """Loads and caches frames from backend/anims/dotoro-boot.gif."""
        if cls._cached_frames is None:
            anims_dir = get_anims_dir()
            boot_gif_path = os.path.join(anims_dir, "dotoro-boot.gif")
            if os.path.isfile(boot_gif_path):
                cls._cached_frames = load_gif_frames(boot_gif_path)
                print(f"[BootApp] Loaded {len(cls._cached_frames)} boot animation frames from dotoro-boot.gif")
            else:
                cls._cached_frames = []
                print(f"[BootApp] Warning: {boot_gif_path} not found!")
        return cls._cached_frames

    def onFocus(self):
        self.currentFrame = 0
        self.lastFrameTime = time.time()
        self.bootComplete = False
        self.hasSignaledComplete = False
        self.needsRedraw = True

    def update(self) -> bool:
        # Switch to Menu app only after the main loop has successfully
        # broadcasted the BOOT_COMPLETE WS message
        if self.bootComplete:
            if self.hasSignaledComplete:
                self.kernel.switchApp("Menu")
                return True
            return False

        if self.frames and len(self.frames) > 0:
            now = time.time()
            frame_delay = max(0.02, self.frames[self.currentFrame].get("delay_ms", 100) / 1000.0)
            if now - self.lastFrameTime >= frame_delay:
                if self.currentFrame + 1 < len(self.frames):
                    self.currentFrame += 1
                    self.lastFrameTime = now
                    self.needsRedraw = True
                else:
                    # Reached the final frame of dotoro-boot.gif
                    self.bootComplete = True
                    self.needsRedraw = True

        if self.needsRedraw:
            self.needsRedraw = False
            return True

        return False

    def render(self, gridManager):
        if self.frames and self.currentFrame < len(self.frames):
            frame_pixels = self.frames[self.currentFrame]["pixels"]
            Graphics.drawImage(gridManager, 0, 0, frame_pixels)
        else:
            gridManager.clearGrid("#000000")

    def onInput(self, key: str):
        # Ignore all key inputs during the boot sequence
        pass
