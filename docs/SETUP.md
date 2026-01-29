# Minecraft AI Builder - Setup Guide

## Prerequisites

- Python 3.9+
- Minecraft Java Edition (for testing)
- Claude API key (from Anthropic)
- RCON-enabled Minecraft server

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/agentlybot/minecraft-ai-builder.git
cd minecraft-ai-builder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the repo root:
```env
ANTHROPIC_API_KEY=your_api_key_here
MINECRAFT_HOST=localhost
MINECRAFT_PORT=25575
MINECRAFT_RCON_PASSWORD=your_rcon_password
```

## Server Setup

### Option A: Local Creative Mode Server (Recommended for Testing)

#### Using Minecraft Launcher
1. Create a new "Creative" world
2. Open to LAN (Pause menu → Open to LAN → Creative mode)
3. Note the port (usually 25565)

#### Enable RCON
1. Stop the server
2. Edit `server.properties`:
   ```
   enable-rcon=true
   rcon.port=25575
   rcon.password=your_secure_password
   ```
3. Restart server

### Option B: Spigot/Paper Server (For Phase 2)

1. Download [Paper](https://papermc.io) (recommended over Spigot)
2. Run: `java -Xmx1024M -Xms1024M -jar paper.jar nogui`
3. Accept EULA
4. Configure server.properties (enable RCON as above)
5. Restart

## Testing Connection

```bash
python3 -c "
from src.server_interface import ServerInterface

server = ServerInterface('localhost', 25575, 'your_password')
try:
    response = server.execute_single('/say Testing...')
    print(f'✅ Connected! Response: {response}')
finally:
    server.close()
"
```

## Quick Start

### 1. Test Spatial Analysis (Claude)

```bash
python3 << 'EOF'
from src.spatial_analyzer import SpatialAnalyzer
import json

analyzer = SpatialAnalyzer()
blueprint = analyzer.analyze("Build a 10x10 oak cabin with a door")
print(json.dumps(blueprint, indent=2))
EOF
```

### 2. Generate Commands

```bash
python3 << 'EOF'
from src.command_generator import CommandGenerator
import json

generator = CommandGenerator()
blueprint = {
    "structure": {"width": 10, "depth": 10, "height": 4},
    "elements": [
        {"type": "wall", "material": "oak_planks", "position": [0, 64, 0], "dimensions": [10, 4, 10]}
    ],
    "build_order": ["wall"]
}
commands = generator.generate(blueprint)
for cmd in commands:
    print(cmd)
EOF
```

### 3. Full Build (End-to-End)

```python
from src.minecraft_builder import MinecraftBuilder

builder = MinecraftBuilder(
    server_host="localhost",
    server_port=25575,
    rcon_password="your_password"
)

result = builder.build("Build a 10x10 oak cabin with a door in front")
print(f"✅ Build complete: {result['blocks_placed']} blocks placed in {result['execution_time']:.2f}s")
```

## Configuration

### server.properties

Critical settings for the builder:
```properties
# Enable remote commands
enable-rcon=true
rcon.port=25575
rcon.password=your_secure_password

# For testing (creative mode)
gamemode=creative
difficulty=peaceful
spawn-protection=0
```

### environment variables

```bash
export ANTHROPIC_API_KEY="sk-..."
export MINECRAFT_HOST="localhost"
export MINECRAFT_PORT=25575
export MINECRAFT_RCON_PASSWORD="your_password"
```

## Troubleshooting

### "Connection refused" error
- **Check:** Is the Minecraft server running?
- **Check:** Is RCON enabled in server.properties?
- **Check:** Is the port correct (default 25575)?
- **Fix:** Restart server and try again

### "Invalid API key" error
- **Check:** Is your ANTHROPIC_API_KEY set correctly?
- **Fix:** Test with: `echo $ANTHROPIC_API_KEY`

### Commands not executing
- **Check:** Are you in Creative mode? (easier for testing)
- **Check:** Do you have permission to build at that location?
- **Fix:** Use `/setworldspawn` to teleport and clear area

### Slow builds / rate limiting
- **Issue:** Minecraft throttles command rate
- **Solution:** Increase rate_limit parameter in execute_commands()
  ```python
  server.execute_commands(commands, rate_limit=0.1)  # 100ms between commands
  ```

## File Structure

```
minecraft-ai-builder/
├── README.md
├── ARCHITECTURE.md
├── requirements.txt
├── .env.example
├── src/
│   ├── minecraft_builder.py      # Main orchestrator
│   ├── spatial_analyzer.py       # Claude integration
│   ├── command_generator.py      # Blueprint → Commands
│   ├── server_interface.py       # RCON client
│   └── utils/
│       └── config.py
├── tests/
│   ├── test_builder.py
│   ├── test_analyzer.py
│   └── test_commands.py
├── docs/
│   ├── SETUP.md (this file)
│   ├── API.md
│   └── BLOCKS.md (Minecraft block reference)
└── examples/
    ├── simple_cabin.json
    ├── house_with_garden.json
    └── village_demo.json
```

## Next Steps

1. ✅ Set up local Minecraft server
2. ✅ Configure RCON and test connection
3. ✅ Run spatial analysis test
4. ✅ Test command generation
5. 🔄 Run full end-to-end build
6. 📝 Refine prompts based on results
7. 🚀 Deploy Phase 2 (Survival mode)

## Phase 2: Survival Mode Setup

Coming soon! This will require:
- Inventory API implementation
- Recipe database
- Crafting simulation
- Material constraint solving

See `ARCHITECTURE.md` for Phase 2 details.

---

**Questions?** Check GitHub Issues or reach out to @agentlybot

**Last Updated:** Jan 28, 2026
