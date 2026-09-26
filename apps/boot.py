import time
from core.appBase import AppBase
from core.graphics import Graphics, FONT_3X5

class BootApp(AppBase):
    def __init__(self, kernel):
        super().__init__()
        self.appName = "Boot"
        self.kernel = kernel
        
        # Timing constants (in seconds)
        self.CRT_WARMUP_DURATION = 0.6
        self.TEXT_TYPING_DURATION = 1.8
        self.PROGRESS_BAR_DURATION = 1.4
        self.COMPLETE_DURATION = 0.7
        
        self.startTime = 0
        self.bootComplete = False  # Set to True when boot animation finishes
        self.hasSignaledComplete = False  # Track if signal was already sent
        self.needsRedraw = True

    def onFocus(self):
        self.startTime = time.time()
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
        
        # Since boot is a continuous animation, we redraw on every frame
        return True

    def render(self, gridManager):
        elapsed = time.time() - self.startTime
        
        # Clear grid to black for the bios screen
        gridManager.clearGrid("#000000")
        
        # Green color for retro terminal vibe
        green = "#00ff66"
        dim_green = "#003311"
        white = "#ffffff"

        # --- Phase 1: CRT Power-on (Warm up animation) ---
        if elapsed < self.CRT_WARMUP_DURATION:
            progress = elapsed / self.CRT_WARMUP_DURATION
            # Horizontal line that starts centered and expands vertically
            line_height = int(progress * 16) # Expand from center row 15/16 outwards
            y_start = max(0, 15 - line_height)
            y_end = min(31, 16 + line_height)
            
            # Draw expanding white/green tube warm up rectangle
            for y in range(y_start, y_end + 1):
                Graphics.drawLine(gridManager, 0, y, 31, y, white if y in (15, 16) else green)
            return

        # Shift elapsed time past the warmup phase
        elapsed -= self.CRT_WARMUP_DURATION

        # --- Phase 2: BIOS Typewriter Text ---
        text_elapsed = elapsed
        lines = [
            "DOTORO BIOS V1.0",
            "MEM 32X32 OK",
            "KERNEL LOAD...",
            "APPS: 5 FOUND"
        ]
        
        # Draw green border around the terminal screen
        Graphics.drawRect(gridManager, 0, 0, 32, 32, dim_green)
        
        # Draw typed characters based on text_elapsed
        # Total duration for typing is self.TEXT_TYPING_DURATION
        total_chars = sum(len(line) for line in lines)
        chars_per_sec = total_chars / self.TEXT_TYPING_DURATION
        chars_to_show = int(text_elapsed * chars_per_sec)
        
        # Distribute chars_to_show across the lines
        chars_counter = 0
        for i, line in enumerate(lines):
            y_pos = 3 + (i * 6) # Y-positions: 3, 9, 15, 21
            if chars_counter >= chars_to_show:
                break
            
            line_chars = len(line)
            if chars_counter + line_chars <= chars_to_show:
                # Fully print line
                Graphics.drawText(gridManager, 2, y_pos, line, green, FONT_3X5)
                chars_counter += line_chars
            else:
                # Partially print line (typewriter effect)
                partial_line = line[:chars_to_show - chars_counter]
                Graphics.drawText(gridManager, 2, y_pos, partial_line, green, FONT_3X5)
                # Draw terminal cursor at end of typing line
                cursor_x = 2 + (len(partial_line) * 4) # 3px font width + 1px space
                if int(time.time() * 5) % 2 == 0:
                    Graphics.drawLine(gridManager, cursor_x, y_pos, cursor_x, y_pos + 4, green)
                break

        # If text is still typing, finish render here
        if text_elapsed < self.TEXT_TYPING_DURATION:
            return

        # Shift elapsed time past typing phase
        elapsed -= self.TEXT_TYPING_DURATION

        # Draw all text fully now that typing is done
        for i, line in enumerate(lines):
            y_pos = 3 + (i * 6)
            Graphics.drawText(gridManager, 2, y_pos, line, green, FONT_3X5)

        # --- Phase 3: Progress Bar Filling ---
        progress_elapsed = elapsed
        if progress_elapsed < self.PROGRESS_BAR_DURATION:
            progress = progress_elapsed / self.PROGRESS_BAR_DURATION
            # Draw filling progress bar at y=27
            Graphics.drawProgressBar(gridManager, 2, 27, 28, progress, green, dim_green)
            return

        # Shift elapsed time past progress bar phase
        elapsed -= self.PROGRESS_BAR_DURATION

        # Draw full progress bar
        Graphics.drawProgressBar(gridManager, 2, 27, 28, 1.0, green, dim_green)

        # --- Phase 4: Complete/Ready display ---
        complete_elapsed = elapsed
        if complete_elapsed < self.COMPLETE_DURATION:
            # Clear text and display centered READY.
            gridManager.clearGrid("#000000")
            Graphics.drawRect(gridManager, 0, 0, 32, 32, dim_green)
            Graphics.drawTextCentered(gridManager, 13, "READY.", green, FONT_3X5)
            
            # Blinking cursor below READY.
            if int(time.time() * 4) % 2 == 0:
                Graphics.drawLine(gridManager, 14, 20, 17, 20, green)
            return

        # --- Sequence Finished ---
        self.bootComplete = True

    def onInput(self, key: str):
        # Ignore all key inputs during the boot sequence
        pass
