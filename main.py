from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from core.gridSystem import GridManager
from core.osKernel import OSKernel
from apps.menu import MenuApp
from apps.timer import TimerApp
from apps.snake import SnakeApp
from apps.themeApp import ThemeApp
import asyncio

# <=== {AppSetup} :: {Initialize fastapi, kernel, and apps} ===>
app = FastAPI()
gridSystem = GridManager()
kernel = OSKernel(gridSystem)

# <=== {RegisterApps} :: {Load all apps into kernel} ===>
kernel.registerApp("Menu", MenuApp(kernel))
kernel.registerApp("Timer", TimerApp(kernel))
kernel.registerApp("Snake", SnakeApp(kernel))
kernel.registerApp("Themes", ThemeApp(kernel))

# Start with Menu
kernel.switchApp("Menu")

# <=== {BroadcastManager} :: {Manage connected clients} ===>
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# <=== {GameLoop} :: {Background task to run app logic} ===>
async def backgroundLoop():
    while True:
        # Run kernel update
        needsSync = kernel.update()
        
        # If visual state changed, broadcast new grid
        if needsSync:
            await manager.broadcast({
                "type": "GRID_UPDATE",
                "grid": gridSystem.getGrid()
            })
            
        # Target ~24 FPS (1/24 = 0.041s)
        await asyncio.sleep(0.041)

# Start background loop on startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(backgroundLoop())

# <=== {WebSocketEndpoint} :: {Handle real-time connection} ===>
@app.websocket("/ws")
async def websocketEndpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send initial state
    await websocket.send_json({
        "type": "GRID_UPDATE",
        "grid": gridSystem.getGrid()
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if "event" in data:
                # Pass input to Kernel
                kernel.handleInput(data["event"])
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
