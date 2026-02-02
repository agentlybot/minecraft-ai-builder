"""
Voxel Blueprints - 3D Array Based Building System

Each blueprint is a 3D array where:
- First dimension (outer) = Y layers (bottom to top)
- Second dimension = Z rows (north to south)
- Third dimension = X columns (west to east)

Cell values:
- "" or None = skip (don't place anything)
- "air" = explicitly clear this block
- "block_name" = place this block type

This format guarantees:
- No gaps in walls
- Exact block placement
- Predictable results every time
"""

from typing import List, Dict, Any, Optional


# === COZY COTTAGE (7x7 base, 6 layers high) ===
COZY_COTTAGE = {
    "name": "cozy_cottage",
    "description": "A cozy cottage with peaked roof, door, and windows",
    "width": 9,  # X
    "depth": 9,  # Z
    "height": 8,  # Y
    "blocks": [
        # Layer 0: Foundation (cobblestone base)
        [
            ["", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", ""],
            ["cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone"],
            ["cobblestone", "cobblestone", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "cobblestone", "cobblestone"],
            ["cobblestone", "cobblestone", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "cobblestone", "cobblestone"],
            ["cobblestone", "cobblestone", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "cobblestone", "cobblestone"],
            ["cobblestone", "cobblestone", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "cobblestone", "cobblestone"],
            ["cobblestone", "cobblestone", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "cobblestone", "cobblestone"],
            ["cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone"],
            ["", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", ""],
        ],
        # Layer 1: First floor walls
        [
            ["", "", "", "", "", "", "", "", ""],
            ["", "stripped_oak_log", "white_concrete", "white_concrete", "oak_door", "white_concrete", "white_concrete", "stripped_oak_log", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "stripped_oak_log", "white_concrete", "white_concrete", "white_concrete", "white_concrete", "white_concrete", "stripped_oak_log", ""],
            ["", "", "", "", "", "", "", "", ""],
        ],
        # Layer 2: Second floor walls
        [
            ["", "", "", "", "", "", "", "", ""],
            ["", "stripped_oak_log", "white_concrete", "white_concrete", "oak_door", "white_concrete", "white_concrete", "stripped_oak_log", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "stripped_oak_log", "white_concrete", "white_concrete", "white_concrete", "white_concrete", "white_concrete", "stripped_oak_log", ""],
            ["", "", "", "", "", "", "", "", ""],
        ],
        # Layer 3: Third floor walls with windows
        [
            ["", "", "", "", "", "", "", "", ""],
            ["", "stripped_oak_log", "white_concrete", "glass_pane", "white_concrete", "glass_pane", "white_concrete", "stripped_oak_log", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "white_concrete", "air", "air", "air", "air", "air", "white_concrete", ""],
            ["", "stripped_oak_log", "white_concrete", "glass_pane", "white_concrete", "glass_pane", "white_concrete", "stripped_oak_log", ""],
            ["", "", "", "", "", "", "", "", ""],
        ],
        # Layer 4: Top of walls / start of roof
        [
            ["", "", "", "", "", "", "", "", ""],
            ["", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", ""],
            ["", "stripped_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_oak_log", ""],
            ["", "stripped_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_oak_log", ""],
            ["", "stripped_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_oak_log", ""],
            ["", "stripped_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_oak_log", ""],
            ["", "stripped_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_oak_log", ""],
            ["", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", "stripped_oak_log", ""],
            ["", "", "", "", "", "", "", "", ""],
        ],
        # Layer 5: Roof layer 1 (stairs)
        [
            ["spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs"],
            ["spruce_stairs", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_stairs"],
            ["", "spruce_stairs", "air", "air", "air", "air", "air", "spruce_stairs", ""],
            ["", "spruce_stairs", "air", "air", "air", "air", "air", "spruce_stairs", ""],
            ["", "spruce_stairs", "air", "air", "air", "air", "air", "spruce_stairs", ""],
            ["", "spruce_stairs", "air", "air", "air", "air", "air", "spruce_stairs", ""],
            ["", "spruce_stairs", "air", "air", "air", "air", "air", "spruce_stairs", ""],
            ["spruce_stairs", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_stairs"],
            ["spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs"],
        ],
        # Layer 6: Roof layer 2
        [
            ["", "", "", "", "", "", "", "", ""],
            ["", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", ""],
            ["", "spruce_stairs", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_stairs", ""],
            ["", "", "spruce_stairs", "air", "air", "air", "spruce_stairs", "", ""],
            ["", "", "spruce_stairs", "air", "air", "air", "spruce_stairs", "", ""],
            ["", "", "spruce_stairs", "air", "air", "air", "spruce_stairs", "", ""],
            ["", "spruce_stairs", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_planks", "spruce_stairs", ""],
            ["", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", ""],
            ["", "", "", "", "", "", "", "", ""],
        ],
        # Layer 7: Roof peak
        [
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "", ""],
            ["", "", "spruce_stairs", "spruce_slab", "spruce_slab", "spruce_slab", "spruce_stairs", "", ""],
            ["", "", "", "spruce_slab", "spruce_slab", "spruce_slab", "", "", ""],
            ["", "", "spruce_stairs", "spruce_slab", "spruce_slab", "spruce_slab", "spruce_stairs", "", ""],
            ["", "", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "spruce_stairs", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
        ],
    ]
}


# === MEDIEVAL TAVERN (11x11 base, 9 layers) ===
MEDIEVAL_TAVERN = {
    "name": "medieval_tavern",
    "description": "A two-story medieval tavern with stone base and half-timbered upper floor",
    "width": 11,
    "depth": 11,
    "height": 10,
    "blocks": [
        # Layer 0: Stone foundation
        [
            ["cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone"],
            ["cobblestone", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", "cobblestone"],
            ["cobblestone", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "cobblestone"],
            ["cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone", "cobblestone"],
        ],
        # Layer 1: Ground floor walls (stone)
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "stone_bricks", "stone_bricks", "stone_bricks", "oak_door", "oak_door", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 2: Ground floor upper (stone with windows)
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "stone_bricks", "glass_pane", "stone_bricks", "oak_door", "oak_door", "stone_bricks", "glass_pane", "stone_bricks", "stone_bricks", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "glass_pane", "air", "air", "air", "air", "air", "air", "air", "glass_pane", ""],
            ["", "stone_bricks", "air", "air", "air", "air", "air", "air", "air", "stone_bricks", ""],
            ["", "stone_bricks", "glass_pane", "stone_bricks", "glass_pane", "stone_bricks", "glass_pane", "stone_bricks", "glass_pane", "stone_bricks", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 3: Ground floor ceiling / second floor base
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stone_bricks", ""],
            ["", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", "stone_bricks", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 4: Second floor walls (half-timbered - jettied)
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["stripped_dark_oak_log", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "stripped_dark_oak_log"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["stripped_dark_oak_log", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "white_terracotta", "stripped_dark_oak_log"],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 5: Second floor upper (with windows)
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["stripped_dark_oak_log", "white_terracotta", "glass_pane", "white_terracotta", "glass_pane", "white_terracotta", "glass_pane", "white_terracotta", "glass_pane", "white_terracotta", "stripped_dark_oak_log"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["glass_pane", "air", "air", "air", "air", "air", "air", "air", "air", "air", "glass_pane"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["glass_pane", "air", "air", "air", "air", "air", "air", "air", "air", "air", "glass_pane"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["glass_pane", "air", "air", "air", "air", "air", "air", "air", "air", "air", "glass_pane"],
            ["white_terracotta", "air", "air", "air", "air", "air", "air", "air", "air", "air", "white_terracotta"],
            ["stripped_dark_oak_log", "white_terracotta", "glass_pane", "white_terracotta", "glass_pane", "white_terracotta", "glass_pane", "white_terracotta", "glass_pane", "white_terracotta", "stripped_dark_oak_log"],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 6: Top of walls / roof start
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "oak_planks", "stripped_dark_oak_log"],
            ["stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log", "stripped_dark_oak_log"],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 7: Roof layer 1
        [
            ["dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs"],
            ["dark_oak_stairs", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_stairs"],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "air", "air", "air", "air", "air", "air", "air", "dark_oak_stairs", ""],
            ["dark_oak_stairs", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_stairs"],
            ["dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs"],
        ],
        # Layer 8: Roof layer 2
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_stairs", ""],
            ["", "", "dark_oak_stairs", "air", "air", "air", "air", "air", "dark_oak_stairs", "", ""],
            ["", "", "dark_oak_stairs", "air", "air", "air", "air", "air", "dark_oak_stairs", "", ""],
            ["", "", "dark_oak_stairs", "air", "air", "air", "air", "air", "dark_oak_stairs", "", ""],
            ["", "", "dark_oak_stairs", "air", "air", "air", "air", "air", "dark_oak_stairs", "", ""],
            ["", "", "dark_oak_stairs", "air", "air", "air", "air", "air", "dark_oak_stairs", "", ""],
            ["", "dark_oak_stairs", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_planks", "dark_oak_stairs", ""],
            ["", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
        # Layer 9: Roof peak
        [
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "", ""],
            ["", "", "dark_oak_stairs", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_stairs", "", ""],
            ["", "", "", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "", "", ""],
            ["", "", "", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "", "", ""],
            ["", "", "", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "", "", ""],
            ["", "", "dark_oak_stairs", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_slab", "dark_oak_stairs", "", ""],
            ["", "", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "dark_oak_stairs", "", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", ""],
        ],
    ]
}


# Blueprint registry
VOXEL_BLUEPRINTS = {
    "cottage": COZY_COTTAGE,
    "cozy cottage": COZY_COTTAGE,
    "oak cottage": COZY_COTTAGE,
    "cabin": COZY_COTTAGE,
    "tavern": MEDIEVAL_TAVERN,
    "medieval tavern": MEDIEVAL_TAVERN,
    "inn": MEDIEVAL_TAVERN,
    "pub": MEDIEVAL_TAVERN,
}


def get_voxel_blueprint(description: str) -> Optional[Dict[str, Any]]:
    """
    Match a description to a voxel blueprint.
    Returns the blueprint dict or None if no match.
    """
    description_lower = description.lower()

    # Check for exact key matches
    for key, blueprint in VOXEL_BLUEPRINTS.items():
        if key in description_lower:
            return blueprint

    # Check for partial matches
    if any(word in description_lower for word in ["cottage", "cozy", "cabin", "hut"]):
        return COZY_COTTAGE
    if any(word in description_lower for word in ["tavern", "inn", "pub", "bar"]):
        return MEDIEVAL_TAVERN

    return None


def voxel_to_commands(blueprint: Dict[str, Any], base_x: int, base_y: int, base_z: int) -> List[str]:
    """
    Convert a voxel blueprint to Minecraft commands.

    Args:
        blueprint: The voxel blueprint dict
        base_x, base_y, base_z: Starting position

    Returns:
        List of Minecraft commands (without leading /)
    """
    commands = []
    blocks = blueprint["blocks"]

    for y_layer, layer in enumerate(blocks):
        for z_row, row in enumerate(layer):
            for x_col, block in enumerate(row):
                if block and block != "":
                    world_x = base_x + x_col
                    world_y = base_y + y_layer
                    world_z = base_z + z_row

                    if block == "air":
                        # Clear block
                        commands.append(f"setblock {world_x} {world_y} {world_z} air")
                    else:
                        # Place block
                        commands.append(f"setblock {world_x} {world_y} {world_z} {block}")

    return commands


def voxel_to_blueprint_format(voxel: Dict[str, Any], base_x: int, base_y: int, base_z: int) -> Dict[str, Any]:
    """
    Convert voxel blueprint to our standard blueprint format for compatibility.
    """
    elements = []
    blocks = voxel["blocks"]

    for y_layer, layer in enumerate(blocks):
        for z_row, row in enumerate(layer):
            for x_col, block in enumerate(row):
                if block and block != "":
                    elements.append({
                        "type": "block",
                        "material": block,
                        "position": [base_x + x_col, base_y + y_layer, base_z + z_row],
                        "dimensions": [1, 1, 1]
                    })

    return {
        "structure": {
            "width": voxel["width"],
            "depth": voxel["depth"],
            "height": voxel["height"],
            "description": voxel["description"],
            "ground_level": base_y
        },
        "elements": elements,
        "build_order": ["block"],
        "is_voxel": True
    }
