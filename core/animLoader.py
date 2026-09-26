import os
import time
from PIL import Image, ImageSequence

def get_anims_dir() -> str:
    """Finds the absolute path to the backend anims folder."""
    # 1. Directory relative to this file (backend/core/ -> backend/anims)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anims_dir = os.path.join(backend_dir, "anims")
    if os.path.isdir(anims_dir):
        return anims_dir

    # 2. Directory relative to current working directory
    cwd_anims = os.path.abspath("anims")
    if os.path.isdir(cwd_anims):
        return cwd_anims

    # 3. dotoro-proto/backend/anims from project root
    cwd_backend_anims = os.path.abspath(os.path.join("backend", "anims"))
    if os.path.isdir(cwd_backend_anims):
        return cwd_backend_anims

    # Fallback / create if missing
    os.makedirs(anims_dir, exist_ok=True)
    return anims_dir


def load_gif_frames(filepath: str) -> list:
    """
    Loads a GIF and extracts frames into 2D pixel grids of hex color strings.
    Supports 320x320 GIF format where each 16x16 pixel is a 19x19 cell with 1px border (pitch 20),
    as well as 16x16 or 32x32 native pixel GIFs.
    """
    frames = []
    try:
        with Image.open(filepath) as gif:
            width, height = gif.size
            
            # Determine grid sizing and sampling coordinates
            if width == 16 and height == 16:
                grid_size = 16
                cell_pitch = 1
                offset = 0
            elif width == 32 and height == 32:
                grid_size = 32
                cell_pitch = 1
                offset = 0
            else:
                # 320x320 grid representing 16x16 with 19px cell + 1px line (20px pitch)
                grid_size = 16
                cell_pitch = max(1, width // grid_size)
                offset = cell_pitch // 2

            default_delay = gif.info.get("duration", 100)
            if not default_delay or default_delay <= 0:
                default_delay = 100

            for frame in ImageSequence.Iterator(gif):
                rgb = frame.convert("RGB")
                pixels = []
                for y in range(grid_size):
                    row = []
                    for x in range(grid_size):
                        if cell_pitch == 1:
                            cx, cy = x, y
                        else:
                            cx = min(width - 1, x * cell_pitch + offset)
                            cy = min(height - 1, y * cell_pitch + offset)
                        
                        r, g, b = rgb.getpixel((cx, cy))[:3]
                        row.append(f"#{r:02x}{g:02x}{b:02x}")
                    pixels.append(row)

                delay_ms = frame.info.get("duration", default_delay)
                if not delay_ms or delay_ms <= 0:
                    delay_ms = default_delay

                frames.append({
                    "pixels": pixels,
                    "delay_ms": delay_ms
                })
    except Exception as e:
        print(f"[AnimLoader] Error loading {filepath}: {e}")

    return frames


class AnimationManager:
    """Manages loading, caching, and hot-reloading animations from the anims folder."""

    def __init__(self, anims_dir: str = None):
        self.anims_dir = anims_dir or get_anims_dir()
        self._cache = {}  # filename -> {"mtime": float, "name": str, "frames": list}

    def reload(self) -> dict:
        """
        Scans the anims directory for GIF files and updates the cache if files are added or modified.
        Returns a dict of { animation_name: frames_list }.
        """
        if not os.path.exists(self.anims_dir):
            return {}

        current_files = set()
        for filename in os.listdir(self.anims_dir):
            if filename.lower().endswith(".gif"):
                filepath = os.path.join(self.anims_dir, filename)
                if os.path.isfile(filepath):
                    current_files.add(filename)
                    mtime = os.path.getmtime(filepath)

                    # Reload if not cached or file was modified
                    cached = self._cache.get(filename)
                    if cached is None or cached["mtime"] != mtime:
                        frames = load_gif_frames(filepath)
                        if frames:
                            # Clean display name: 'edited-bootup.gif' -> 'Bootup' or 'Edited-Bootup'
                            base_name = os.path.splitext(filename)[0]
                            clean_name = base_name.replace("_", " ").replace("-", " ").title()
                            self._cache[filename] = {
                                "mtime": mtime,
                                "name": clean_name,
                                "raw_name": base_name,
                                "frames": frames
                            }
                            print(f"[AnimLoader] Loaded animation '{clean_name}' ({len(frames)} frames) from {filename}")

        # Remove deleted files from cache
        for filename in list(self._cache.keys()):
            if filename not in current_files:
                del self._cache[filename]

        # Return dict mapping name -> frames
        animations = {}
        for filename, data in self._cache.items():
            animations[data["name"]] = data["frames"]

        return animations
