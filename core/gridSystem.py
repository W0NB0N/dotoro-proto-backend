# <=== {GridSystem} :: {Manages the 16x16 pixel display state} ===>
class GridManager:
    
    # <=== {Constructor} :: {Initialize 32x32 black grid} ===>
    def __init__(self):
        self.width = 32
        self.height = 32
        # Start with all black pixels
        self.pixels = [["#000000" for _ in range(32)] for _ in range(32)]


    # <=== {ClearGrid} :: {Reset all pixels to color} ===>
    def clearGrid(self, color: str = "#000000"):
        self.pixels = [[color for _ in range(self.width)] for _ in range(self.height)]

    # <=== {SetPixel} :: {Update single pixel color safely} ===>
    def setPixel(self, x: int, y: int, color: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    # <=== {GetGrid} :: {Return current grid state} ===>
    def getGrid(self) -> list[list[str]]:
        return self.pixels

    # <=== {GetFlatGrid} :: {Return flattened 1D list of hex codes} ===>
    def getFlatGrid(self) -> list[str]:
        return [pixel for row in self.pixels for pixel in row]

