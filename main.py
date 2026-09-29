from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import dataclass, field
from uuid import uuid4
import asyncio
import time

from core.gridSystem import GridManager
from core.osKernel import OSKernel
from core.animLoader import AnimationManager
from apps.menu import MenuApp
from apps.timer import TimerApp
from apps.snake import SnakeApp
from apps.themeApp import ThemeApp
from apps.gallery import GalleryApp
from apps.boot import BootApp

# <=== {AppSetup} :: {Initialize fastapi application} ===>
app = FastAPI(title="Dotoro Backend")

# Enable CORS for deployed frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared read-only animation manager (cached GIF frames shared across all sessions)
shared_anim_manager = AnimationManager()


# <=== {SessionFactory} :: {Create an isolated kernel and apps for a connection} ===>
def create_session():
    """Instantiate a dedicated GridManager, OSKernel, and app instances for one client."""
    grid = GridManager()
    kernel = OSKernel(grid)

    kernel.registerApp("Boot", BootApp(kernel))
    kernel.registerApp("Menu", MenuApp(kernel))
    kernel.registerApp("Timer", TimerApp(kernel))
    kernel.registerApp("Snake", SnakeApp(kernel))
    kernel.registerApp("Themes", ThemeApp(kernel))

    # GalleryApp reuses the shared cached animation manager
    kernel.registerApp("Gallery", GalleryApp(kernel, anim_manager=shared_anim_manager))

    # Start each session with the BIOS bootup sequence
    kernel.switchApp("Boot")

    return kernel, grid


# <=== {SessionModel} :: {Per-client state container} ===>
@dataclass
class Session:
    session_id: str
    kernel: OSKernel
    grid: GridManager
    websocket: WebSocket
    loop_task: asyncio.Task = None
    created_at: float = field(default_factory=time.time)
    last_input_at: float = field(default_factory=time.time)


# <=== {SessionManager} :: {Manage lifecycle and isolation of client sessions} ===>
class SessionManager:
    def __init__(self, idle_timeout_seconds: int = 300):
        self.sessions: dict[str, Session] = {}
        self.idle_timeout = idle_timeout_seconds  # 5 minutes default

    def create(self, session_id: str, kernel: OSKernel, grid: GridManager, websocket: WebSocket) -> Session:
        session = Session(
            session_id=session_id,
            kernel=kernel,
            grid=grid,
            websocket=websocket
        )
        self.sessions[session_id] = session
        print(f"[Session] Created: {session_id} (active: {len(self.sessions)})")
        return session

    def destroy(self, session_id: str):
        session = self.sessions.pop(session_id, None)
        if session and session.loop_task and not session.loop_task.done():
            session.loop_task.cancel()
        print(f"[Session] Destroyed: {session_id} (active: {len(self.sessions)})")

    def touch(self, session_id: str):
        """Record activity timestamp on user input."""
        if session_id in self.sessions:
            self.sessions[session_id].last_input_at = time.time()

    def get_idle_sessions(self) -> list[str]:
        """Find session IDs that have been inactive longer than idle_timeout."""
        now = time.time()
        return [
            sid for sid, s in self.sessions.items()
            if now - s.last_input_at > self.idle_timeout
        ]

    @property
    def count(self) -> int:
        return len(self.sessions)


session_manager = SessionManager(idle_timeout_seconds=300)


# <=== {HealthCheck} ===>
@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": "dotoro-backend",
        "active_sessions": session_manager.count
    }


# <=== {IdleReaper} :: {Periodic background cleanup for abandoned sessions} ===>
async def idle_reaper():
    """Periodically closes sessions that have had no input activity for 5+ minutes."""
    while True:
        try:
            await asyncio.sleep(60)
            idle_ids = session_manager.get_idle_sessions()
            for sid in idle_ids:
                session = session_manager.sessions.get(sid)
                if session:
                    print(f"[Reaper] Session {sid} timed out due to inactivity. Closing connection...")
                    try:
                        await session.websocket.close(code=4001, reason="Session idle timeout")
                    except Exception:
                        pass
                    session_manager.destroy(sid)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Reaper] Error during idle cleanup: {e}")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(idle_reaper())


# <=== {WebSocketEndpoint} :: {Dedicated session connection handler} ===>
@app.websocket("/ws")
async def websocketEndpoint(websocket: WebSocket):
    await websocket.accept()

    session_id = str(uuid4())[:8]
    kernel, grid = create_session()
    session = session_manager.create(session_id, kernel, grid, websocket)

    # Per-session background game loop running at ~24 FPS
    async def session_loop():
        try:
            while True:
                # Update kernel state for this specific session
                needs_sync = kernel.update()

                if needs_sync:
                    await websocket.send_json({
                        "type": "GRID_UPDATE",
                        "grid": grid.getFlatGrid(),
                        "theme": kernel.themeManager.toClientPayload()
                    })

                # Check if Boot sequence completed and needs sound signal
                if (kernel.activeApp
                    and kernel.activeApp.appName == "Boot"
                    and kernel.activeApp.bootComplete
                    and not kernel.activeApp.hasSignaledComplete):
                    kernel.activeApp.hasSignaledComplete = True
                    await websocket.send_json({
                        "type": "BOOT_COMPLETE"
                    })

                await asyncio.sleep(0.041)  # ~24 FPS
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Session {session_id}] Loop stopped: {e}")

    session.loop_task = asyncio.create_task(session_loop())

    try:
        # Send initial grid state
        await websocket.send_json({
            "type": "GRID_UPDATE",
            "grid": grid.getFlatGrid(),
            "theme": kernel.themeManager.toClientPayload()
        })

        # Process incoming user input events for this session
        while True:
            data = await websocket.receive_json()
            if "event" in data:
                session_manager.touch(session_id)
                kernel.handleInput(data["event"])
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        session_manager.destroy(session_id)
