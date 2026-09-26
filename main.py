from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from core.gridSystem import GridManager
from core.osKernel import OSKernel
from apps.menu import MenuApp
from apps.timer import TimerApp
from apps.snake import SnakeApp
from apps.themeApp import ThemeApp
from apps.gallery import GalleryApp
from apps.boot import BootApp
import asyncio

# <=== {AppSetup} :: {Initialize fastapi, kernel, and apps} ===>
app = FastAPI(title="Dotoro Backend")

# Enable CORS for deployed frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "dotoro-backend"}

gridSystem = GridManager()
kernel = OSKernel(gridSystem)

# <=== {RegisterApps} :: {Load all apps into kernel} ===>
kernel.registerApp("Boot", BootApp(kernel))
kernel.registerApp("Menu", MenuApp(kernel))
kernel.registerApp("Timer", TimerApp(kernel))
kernel.registerApp("Snake", SnakeApp(kernel))
kernel.registerApp("Themes", ThemeApp(kernel))
kernel.registerApp("Gallery", GalleryApp(kernel))

# Start with Boot BIOS sequence
kernel.switchApp("Boot")


# <=== {BroadcastManager} :: {Manage connected clients} ===>
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# <=== {GameLoop} :: {Background task to run app logic} ===>
async def backgroundLoop():
    while True:
        try:
            # Run kernel update
            needsSync = kernel.update()
            
            # If visual state changed, broadcast new grid
            if needsSync:
                await manager.broadcast({
                    "type": "GRID_UPDATE",
                    "grid": gridSystem.getFlatGrid(),
                    "theme": kernel.themeManager.toClientPayload()
                })

            # Check if Boot App has completed and needs to play sound
            if kernel.activeApp and kernel.activeApp.appName == "Boot":
                if kernel.activeApp.bootComplete and not kernel.activeApp.hasSignaledComplete:
                    kernel.activeApp.hasSignaledComplete = True
                    await manager.broadcast({
                        "type": "BOOT_COMPLETE"
                    })
        except Exception as e:
            print(f"Error in backgroundLoop: {e}")
                
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
    try:
        # Send initial state
        await websocket.send_json({
            "type": "GRID_UPDATE",
            "grid": gridSystem.getFlatGrid(),
            "theme": kernel.themeManager.toClientPayload()
        })
        
        while True:
            data = await websocket.receive_json()
            if "event" in data:
                # Pass input to Kernel
                kernel.handleInput(data["event"])
    except (WebSocketDisconnect, Exception):
        manager.disconnect(websocket)

