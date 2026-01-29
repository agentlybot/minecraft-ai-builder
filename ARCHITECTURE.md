# Minecraft AI Builder - Architecture

## System Design

### Input Pipeline

```
┌─────────────────────────────────────┐
│   User Natural Language Input       │
│   "Build a 10x10 oak cabin"         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│   Claude LLM Integration                    │
│   - Parse spatial requirements              │
│   - Understand material references          │
│   - Design structure in 3D space            │
│   - Generate step-by-step build plan        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│   Minecraft Command Generator               │
│   - Convert design to /setblock commands    │
│   - Batch optimize fills with /fill        │
│   - Handle relative positioning             │
│   - Validate command syntax                 │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│   Minecraft Server Interface                │
│   - Send commands via mcrcon or API         │
│   - Handle execution sequencing             │
│   - Rate limiting (avoid chat flood)        │
│   - Error recovery                          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│   Game State (Phase 2)                      │
│   - Read player inventory                   │
│   - Check available resources               │
│   - Update crafting suggestions             │
└─────────────────────────────────────────────┘
```

## Core Components

### 1. SpatialAnalyzer (Claude Integration)

**Responsibility:** Parse natural language descriptions into spatial blueprints

**Input:**
```
{
  "description": "Build a 10x10 oak cabin with a door in front and windows",
  "player_pos": [0, 64, 0],
  "available_materials": null  // Phase 2: inventory list
}
```

**Output:**
```
{
  "structure": {
    "width": 10,
    "depth": 10,
    "height": 4,
    "base_material": "oak_planks",
    "roof_material": "dark_oak_stairs"
  },
  "elements": [
    {"type": "wall", "material": "oak_planks", "dimensions": [10, 4, 10]},
    {"type": "door", "material": "oak_door", "position": [5, 1, 0], "facing": "south"},
    {"type": "window", "material": "glass_pane", "positions": [[2, 2, 0], [7, 2, 0], ...]}
  ],
  "build_order": ["foundation", "walls", "roof", "door", "windows", "interior"]
}
```

### 2. CommandGenerator

**Responsibility:** Convert spatial blueprints to Minecraft commands

**Methods:**
- `generate_fill_commands()` - Optimize large areas with /fill
- `generate_setblock_commands()` - Precise placement with /setblock
- `batch_commands()` - Group commands for efficient sending
- `validate_syntax()` - Ensure all commands are legal

**Example Output:**
```bash
/fill 0 64 0 10 68 10 oak_planks
/setblock 5 64 0 oak_door[facing=south]
/setblock 2 66 0 glass_pane
/setblock 7 66 0 glass_pane
...
```

### 3. MinecraftBuilder (Orchestrator)

**Responsibility:** Manage the entire build pipeline

**Flow:**
1. Accept user input
2. Call SpatialAnalyzer (Claude)
3. Call CommandGenerator
4. Send commands to server
5. Monitor progress & report status

## Data Flow (Phase 1)

```
User Input
    ↓
SpatialAnalyzer.parse()  (Claude API call)
    ↓
CommandGenerator.generate()  (Transform to commands)
    ↓
MinecraftBuilder.build()  (Execute on server)
    ↓
Return: Build status & completion time
```

## Server Integration

### Option A: mcrcon (Remote Console)
- **Pros:** No server mod needed, works with any server
- **Cons:** Slower, requires rcon password
- **Good for:** Testing, quick scripts

### Option B: Paper/Spigot Plugin
- **Pros:** Direct API access, faster, can read state
- **Cons:** Requires server setup, plugin development
- **Good for:** Phase 2, survival mode with inventory checking

### Option C: Direct World Manipulation
- **Pros:** Fastest, direct NBT editing
- **Cons:** Server must be offline, complex
- **Good for:** Batch operations, offline testing

**Decision for Phase 1:** Start with mcrcon for simplicity

## Claude Prompt Design

The system prompt will guide Claude to:

1. **Understand spatial reasoning**
   - Convert text to 3D coordinates
   - Handle relative directions (north, south, up, down)
   - Respect chunk boundaries

2. **Optimize for Minecraft constraints**
   - Max command length: ~32k characters
   - Command rate limiting: ~1-2 per tick
   - Block type availability

3. **Generate clean output**
   - JSON structure (easy to parse)
   - Step-by-step build instructions
   - Error messages if request is impossible

## Phase 2: Survival Mode Extensions

### Inventory System
```
Player Inventory:
- oak_planks: 64
- oak_log: 32
- glass: 16
- oak_door: 2

Claude Task:
"Build an oak cabin using available materials"
→ Adjust design to fit inventory
→ Suggest what to craft next
```

### Recipe Database
```
oak_planks × 4 ← oak_log × 1
oak_stairs × 8 ← oak_planks × 6
oak_door × 3 ← oak_planks × 6
```

### Constraint-Aware Planning
```
Request: "Build a large mansion"
Available: 64 oak planks

Claude Output:
"Not enough oak planks (need 256, have 64).
Suggestions:
1. Build smaller version (5x5 instead of 10x10)
2. Use alternative materials (birch, spruce)
3. Mine oak logs and craft them (takes ~5 min per stack)
4. Just craft more at your current station"
```

## Testing Strategy

- **Unit Tests:** Command generation, syntax validation
- **Integration Tests:** Full pipeline with mock Minecraft server
- **Live Tests:** Actual Minecraft server (creative mode first)
- **Prompt Testing:** Verify Claude generates valid designs

## Deployment

**Phase 1:**
- Local Minecraft server (single-player Creative Mode)
- Python script + Claude API

**Phase 2:**
- Option A: Cloud-hosted Minecraft server
- Option B: Local Paper/Spigot plugin
- Add web UI for non-technical users

## Performance Targets

- **Input to first block placed:** < 5 seconds (Phase 1)
- **Large structure (10x10x10):** < 30 seconds (Phase 1)
- **Survival mode planning:** < 10 seconds (Phase 2)

## Open Questions

1. **Server choice:** Spigot or Paper? Version?
2. **Account:** Shared test account or multiple?
3. **State tracking:** How to monitor build progress?
4. **Error recovery:** What if command fails mid-build?
5. **Cost:** Claude API usage estimates?
6. **Scaling:** Multiple players / simultaneous builds?

---

**Last Updated:** Jan 28, 2026
