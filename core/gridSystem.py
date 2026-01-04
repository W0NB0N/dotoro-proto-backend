# <=== {GridSystem} :: {Manages the 16x16 pixel display state} ===>
class GridManager:
    
    # <=== {Constructor} :: {Initialize 16x16 black grid} ===>
    def __init__(self):
        self.width = 16
        self.height = 16
        # Start with all black pixels
        self.pixels = [["#000000" for _ in range(16)] for _ in range(16)]

    # <=== {ClearGrid} :: {Reset all pixels to black} ===>
    def clearGrid(self):
        self.pixels = [["#000000" for _ in range(16)] for _ in range(16)]

    # <=== {SetPixel} :: {Update single pixel color safely} ===>
    def setPixel(self, x: int, y: int, color: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    # <=== {GetGrid} :: {Return current grid state} ===>
    def getGrid(self) -> list[list[str]]:
        return self.pixels
