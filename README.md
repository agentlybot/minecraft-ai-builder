# Minecraft AI Builder

NLP-powered Minecraft builder that uses Claude to parse natural language descriptions and generate Minecraft commands.

## Overview

Transform text descriptions into live Minecraft builds using Claude's spatial reasoning and natural language understanding.

**Example:**
```
User: "Build me a 10x10 oak cabin with a door in the front and windows on the sides"
→ Claude parses → Generates /setblock commands → Live build appears
```

## Project Phases

### Phase 1: Creative Mode (POC) - 1-2 weeks
- No material limitations
- Pure NLP-to-structure translation
- Test spatial reasoning & architecture understanding
- **Goal:** Prove the concept works

### Phase 2: Survival Mode (Production) - 2-3 weeks after Phase 1
- Inventory checking (what materials you have)
- Recipe database (what crafts into what)
- Constraint-aware building suggestions
- Resource optimization
- **Goal:** Production-ready builder assistant

## Architecture

```
Natural Language Input
    ↓
Claude LLM (parse + spatial design)
    ↓
Minecraft Command Generator (/fill, /setblock, etc.)
    ↓
Minecraft Server (Java Edition)
    ↓
Live Build in Game
```

## Tech Stack

- **AI/Reasoning:** Claude API
- **Server:** Minecraft Java Edition (Spigot/Paper TBD)
- **Control:** mcrcon or direct command API
- **Language:** Python (initial) / Node.js (TBD)

## Quick Start

(Setup docs coming soon)

## File Structure

```
minecraft-ai-builder/
├── README.md
├── ARCHITECTURE.md
├── src/
│   ├── minecraft_builder.py      # Main builder class
│   ├── command_generator.py      # /setblock, /fill translator
│   ├── spatial_analyzer.py       # Claude integration for parsing
│   └── utils/
│       └── config.py             # Server/account setup
├── tests/
│   └── test_builder.py
├── docs/
│   ├── SETUP.md                  # Server setup guide
│   └── API.md                    # Builder API reference
└── .github/
    └── workflows/
        └── tests.yml
```

## Key Questions

- [ ] Server: Spigot or Paper?
- [ ] Deployment: Local or cloud?
- [ ] Test account: Create dedicated account or use your main?
- [ ] Game state capture: How to read back inventory/world state?
- [ ] Phase 2: Full recipe database or API-based lookup?

## Getting Started

See [SETUP.md](./docs/SETUP.md) for server configuration and initial development setup.

## License

MIT

---

**Project Start:** Jan 28, 2026  
**Status:** Phase 1 - Architecture & Mockup
