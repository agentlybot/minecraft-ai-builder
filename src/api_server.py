"""
FastAPI server for Minecraft AI Builder

Exposes the building functionality as a REST API for the web frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import re
from dotenv import load_dotenv

from minecraft_builder import MinecraftBuilder

load_dotenv()

app = FastAPI(title="Craft Architect API", version="1.0.0")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://192.168.7.191:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Server connection settings (will come from user config in production)
RCON_HOST = os.getenv("RCON_HOST", "localhost")
RCON_PORT = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "aibuilder123")

# Build state tracking with full memory
class BuildState:
    def __init__(self):
        self.last_build: Optional[Dict[str, Any]] = None
        self.build_history: List[Dict[str, Any]] = []  # Keep history of all builds
        self.next_x: int = 10  # Starting X position
        self.next_z: int = 10  # Starting Z position
        self.ground_y: int = -60  # Superflat ground level
        self.min_spacing: int = 5  # Minimum blocks between structures

    def get_next_position(self) -> List[int]:
        """Get position for next build with proper spacing."""
        return [self.next_x, self.ground_y, self.next_z]

    def record_build(self, position: List[int], blueprint: Dict[str, Any], description: str):
        """Record a completed build and update next position."""
        structure = blueprint.get("structure", {})
        width = structure.get("width", 15)
        depth = structure.get("depth", 15)
        height = structure.get("height", 10)

        build_record = {
            "description": description,
            "position": position,
            "blueprint": blueprint,
            "structure": structure,
            "bounds": {
                "min_x": position[0],
                "max_x": position[0] + width,
                "min_y": position[1],
                "max_y": position[1] + height,
                "min_z": position[2],
                "max_z": position[2] + depth,
                "width": width,
                "depth": depth,
                "height": height,
            },
            "building_type": self._detect_building_type(description),
        }

        self.last_build = build_record
        self.build_history.append(build_record)

        # Update next position AFTER build, based on actual dimensions
        self.next_x = position[0] + width + self.min_spacing + 10

        # Wrap to new row if too far
        if self.next_x > 150:
            self.next_x = 10
            self.next_z = position[2] + depth + self.min_spacing + 15

    def _detect_building_type(self, description: str) -> str:
        """Detect the type of building from description."""
        desc_lower = description.lower()
        if any(w in desc_lower for w in ["cottage", "cabin", "hut"]):
            return "cottage"
        elif any(w in desc_lower for w in ["tavern", "inn", "pub"]):
            return "tavern"
        elif any(w in desc_lower for w in ["house", "home"]):
            return "house"
        elif any(w in desc_lower for w in ["castle", "fortress"]):
            return "castle"
        elif any(w in desc_lower for w in ["tower"]):
            return "tower"
        return "structure"

    def is_addition_request(self, description: str) -> bool:
        """Check if this is a request to add to existing structure."""
        # First check if it's clearly a NEW structure request
        new_structure_patterns = [
            r'\bbuild\s+(a|me|another)\b', r'\bcreate\s+(a|me|another)\b',
            r'\bmake\s+(a|me|another)\b', r'\bnew\b',
            r'\bcottage\b', r'\bhouse\b', r'\btavern\b', r'\bcastle\b',
            r'\btower\b', r'\bchurch\b', r'\bbridge\b', r'\bshop\b'
        ]
        desc_lower = description.lower()

        # If it looks like a new structure, it's NOT an addition
        if any(re.search(p, desc_lower) for p in new_structure_patterns):
            return False

        # Check for addition patterns (only if we have an existing build)
        addition_patterns = [
            r'\badd\s+(a|some|the)\b', r'\bput\s+(a|some|the)\b',
            r'\bplace\s+(a|some|the)\b', r'\binclude\b',
            r'\binside\b', r'\binterior\b', r'\bfurnish\b', r'\bdecorate\b',
            r'\bnext to (the|my|this)\b', r'\bbeside (the|my|this)\b'
        ]
        return any(re.search(p, desc_lower) for p in addition_patterns) and self.last_build is not None

    def is_interior_request(self, description: str) -> bool:
        """Check if this is a request for interior placement."""
        interior_words = ["inside", "interior", "within", "in the", "indoors"]
        desc_lower = description.lower()
        return any(word in desc_lower for word in interior_words)

    def get_interior_position(self) -> Optional[List[int]]:
        """Get a position inside the last built structure."""
        if not self.last_build:
            return None

        bounds = self.last_build["bounds"]
        # Center of the building, on the ground floor
        interior_x = bounds["min_x"] + bounds["width"] // 2
        interior_y = bounds["min_y"] + 1  # One above floor
        interior_z = bounds["min_z"] + bounds["depth"] // 2

        return [interior_x, interior_y, interior_z]

    def get_context_for_addition(self) -> str:
        """Get context string about the last build for AI additions."""
        if not self.last_build:
            return ""

        bounds = self.last_build["bounds"]
        building_type = self.last_build["building_type"]

        return (
            f"CONTEXT: The player's {building_type} is at position "
            f"[{bounds['min_x']}, {bounds['min_y']}, {bounds['min_z']}]. "
            f"Building bounds: X from {bounds['min_x']} to {bounds['max_x']}, "
            f"Y from {bounds['min_y']} to {bounds['max_y']}, "
            f"Z from {bounds['min_z']} to {bounds['max_z']}. "
            f"Interior floor is at Y={bounds['min_y'] + 1}. "
            f"Place additions INSIDE these bounds if 'interior' is mentioned."
        )

build_state = BuildState()


class BuildRequest(BaseModel):
    description: str
    player_pos: Optional[List[int]] = None


class BuildResponse(BaseModel):
    status: str
    description: str
    blocks_placed: int
    execution_time: float
    message: str
    errors: List[str] = []


class ServerStatus(BaseModel):
    connected: bool
    host: str
    port: int
    message: str


@app.get("/")
async def root():
    return {"message": "Craft Architect API is running!", "version": "1.0.0"}


@app.get("/status", response_model=ServerStatus)
async def get_status():
    """Check if we can connect to the Minecraft server."""
    try:
        builder = MinecraftBuilder(RCON_HOST, RCON_PORT, RCON_PASSWORD)
        # Try a simple command to test connection
        result = builder.server.execute_single("say 🎮 AI Builder ready! Describe what you want to build.")
        return ServerStatus(
            connected=True,
            host=RCON_HOST,
            port=RCON_PORT,
            message="Connected to Minecraft server"
        )
    except Exception as e:
        return ServerStatus(
            connected=False,
            host=RCON_HOST,
            port=RCON_PORT,
            message=f"Failed to connect: {str(e)}"
        )


@app.post("/build", response_model=BuildResponse)
async def build(request: BuildRequest):
    """
    Execute a build request on the Minecraft server.

    Takes a natural language description and builds it in the world.
    Steve remembers the last build so additions go in the right place.
    """
    try:
        builder = MinecraftBuilder(RCON_HOST, RCON_PORT, RCON_PASSWORD)

        # Check if this is an addition to existing structure
        is_addition = build_state.is_addition_request(request.description)
        is_interior = build_state.is_interior_request(request.description)

        if is_addition and build_state.last_build:
            # Addition to existing structure
            last_build = build_state.last_build
            building_type = last_build["building_type"]
            bounds = last_build["bounds"]

            if is_interior:
                # Interior addition - position inside the building
                build_pos = build_state.get_interior_position()
                builder.server.execute_single(f"say 🔧 Adding interior element to your {building_type}...")
            else:
                # Exterior addition - position at the building
                build_pos = last_build["position"]
                builder.server.execute_single(f"say 🔧 Adding to your {building_type}...")

            # Enhanced description with full context
            context = build_state.get_context_for_addition()
            enhanced_description = (
                f"{request.description}. {context} "
                f"IMPORTANT: Only generate the NEW element being added. "
                f"Do NOT regenerate the {building_type} itself."
            )

            # Don't teleport for additions - player is already there
            skip_teleport = True
        else:
            # New structure - get player position and build where they're looking
            player_data = builder.server.get_player_position()

            if player_data:
                # Build 15 blocks in front of where player is looking
                distance = 15
                build_x = int(player_data["x"] + player_data["dir_x"] * distance)
                build_z = int(player_data["z"] + player_data["dir_z"] * distance)
                # Always use superflat ground level Y=-60
                ground_y = -60
                build_pos = [build_x, ground_y, build_z]
                builder.server.execute_single(f"say 🏰 Building where you're looking: X:{build_x} Z:{build_z}")
            else:
                # Fallback to auto-position if can't get player data
                # Always use fresh position to avoid overlaps
                build_pos = build_state.get_next_position()
                builder.server.execute_single(f"say ⚠️ Couldn't get player position, building at X:{build_pos[0]} Z:{build_pos[2]}")
                builder.server.execute_single(f"say 💡 Tip: Stand where you want to build and look in that direction")

            enhanced_description = request.description
            skip_teleport = False

        # Execute the build
        result = builder.build(enhanced_description, build_pos)

        if result["status"] == "success":
            # Record this build for future reference (only for new structures)
            blueprint = result.get("blueprint", {})
            if not is_addition:
                build_state.record_build(build_pos, blueprint, request.description)

            # Get structure dimensions for teleport
            structure = blueprint.get("structure", {})
            width = structure.get("width", 10)
            depth = structure.get("depth", 10)

            # Teleport player to the build location (unless it's an addition)
            if not skip_teleport:
                tp_x = build_pos[0] + width // 2
                tp_y = build_pos[1] + 1  # One block above ground
                tp_z = build_pos[2] - 2  # In front of the build
                builder.server.execute_single(f"tp @a {tp_x} {tp_y} {tp_z}")

            # Announce completion
            if is_addition:
                builder.server.execute_single(f"say ✅ Addition complete!")
            else:
                builder.server.execute_single(f"say ✅ Build complete! Teleporting you there now!")

            return BuildResponse(
                status="success",
                description=request.description,
                blocks_placed=result["blocks_placed"],
                execution_time=result["execution_time"],
                message=f"Build complete! Placed {result['blocks_placed']} blocks in {result['execution_time']:.2f}s",
                errors=result.get("errors", [])
            )
        else:
            raise HTTPException(status_code=500, detail="Build failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
