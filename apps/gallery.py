import time
from core.appBase import AppBase
from core.graphics import Graphics
from core.images import IMAGES
from core.animLoader import AnimationManager

# <=== {GalleryApp} :: {App to display custom pixel art images and GIF animations} ===>
class GalleryApp(AppBase):
    
    def __init__(self, kernel, anim_manager=None):
        super().__init__()
        self.appName = "Gallery"
        self.kernel = kernel
        self.animManager = anim_manager if anim_manager is not None else AnimationManager()
        
        self.items = [] # list of {"name": str, "type": "image"|"animation", ...}
        self.currentIndex = 0
        self.maxIndex = 0
        self.currentFrame = 0
        self.lastFrameTime = 0.0
        self.needsRedraw = True

        self.loadItems()

    def loadItems(self):
        """Scans static images and dynamic GIF animations from anims folder."""
        # Remember currently selected item name to restore position if possible
        selected_name = self.items[self.currentIndex]["name"] if self.items and self.currentIndex < len(self.items) else None

        new_items = []

        # 1. Add static images from IMAGES dictionary
        for name, img_data in IMAGES.items():
            new_items.append({
                "name": name,
                "type": "image",
                "data": img_data
            })

        # 2. Add GIF animations from backend/anims/
        animations = self.animManager.reload()
        for anim_name, frames in animations.items():
            if frames:
                new_items.append({
                    "name": anim_name,
                    "type": "animation",
                    "frames": frames
                })

        self.items = new_items
        self.maxIndex = max(0, len(self.items) - 1)

        # Restore index or clamp
        if selected_name:
            matching = [i for i, item in enumerate(self.items) if item["name"] == selected_name]
            if matching:
                self.currentIndex = matching[0]
            else:
                self.currentIndex = min(self.currentIndex, self.maxIndex)
        else:
            self.currentIndex = min(self.currentIndex, self.maxIndex)

    def onFocus(self):
        self.loadItems()
        self.currentFrame = 0
        self.lastFrameTime = time.time()
        self.needsRedraw = True

    def update(self) -> bool:
        if not self.items:
            if self.needsRedraw:
                self.needsRedraw = False
                return True
            return False

        currentItem = self.items[self.currentIndex]

        # Handle animated GIF frame advancement
        if currentItem["type"] == "animation":
            frames = currentItem["frames"]
            if len(frames) > 1:
                now = time.time()
                # Get frame delay in seconds (minimum 20ms to prevent division by zero/hyper-speed)
                frame_delay = max(0.02, frames[self.currentFrame].get("delay_ms", 100) / 1000.0)
                if now - self.lastFrameTime >= frame_delay:
                    self.currentFrame = (self.currentFrame + 1) % len(frames)
                    self.lastFrameTime = now
                    self.needsRedraw = True

        if self.needsRedraw:
            self.needsRedraw = False
            return True

        return False

    def render(self, gridManager):
        theme = self.kernel.themeManager.get()
        gridManager.clearGrid(theme.background)

        if not self.items:
            return

        currentItem = self.items[self.currentIndex]

        if currentItem["type"] == "image":
            Graphics.drawImage(gridManager, 0, 0, currentItem["data"])
        elif currentItem["type"] == "animation":
            frames = currentItem["frames"]
            if frames:
                current_pixel_data = frames[self.currentFrame]["pixels"]
                Graphics.drawImage(gridManager, 0, 0, current_pixel_data)

    def onInput(self, key: str):
        if not self.items:
            return

        if key == "Left":
            self.currentIndex = max(0, self.currentIndex - 1)
            self.currentFrame = 0
            self.lastFrameTime = time.time()
            self.needsRedraw = True
            print(f"Gallery switched left to: {self.items[self.currentIndex]['name']}")
        elif key == "Right":
            self.currentIndex = min(self.maxIndex, self.currentIndex + 1)
            self.currentFrame = 0
            self.lastFrameTime = time.time()
            self.needsRedraw = True
            print(f"Gallery switched right to: {self.items[self.currentIndex]['name']}")
        elif key == "Enter":
            pass
