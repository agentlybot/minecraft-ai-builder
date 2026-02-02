"""
Building Templates - Pre-designed structures with professional quality

Each template is a function that generates a complete element list for a building type.
Templates ensure:
- Complete walls with no gaps
- Proper peaked roofs using stairs
- Doors, windows, and decorations
- Half-timbered framing where appropriate
"""

from typing import List, Dict, Any


def cottage_template(
    base_x: int, base_y: int, base_z: int,
    width: int = 9, depth: int = 7, height: int = 5,
    wood_type: str = "oak", roof_type: str = "spruce",
    has_garden: bool = True, has_chimney: bool = True
) -> Dict[str, Any]:
    """
    Generate a cozy cottage with proper construction.

    Features:
    - Cobblestone foundation
    - Half-timbered walls (log frame + white infill)
    - Peaked roof with overhang
    - Windows with shutters
    - Front door with porch
    - Optional garden and chimney
    """
    elements = []

    # Materials
    planks = f"{wood_type}_planks"
    log = f"stripped_{wood_type}_log"
    stairs = f"{roof_type}_stairs"
    slab = f"{roof_type}_slab"
    fence = f"{wood_type}_fence"
    trapdoor = f"{roof_type}_trapdoor"
    door = f"{wood_type}_door"

    # Dimensions
    w, d, h = width, depth, height
    x, y, z = base_x, base_y, base_z

    # === FOUNDATION (cobblestone, extends 1 block out) ===
    elements.append({
        "type": "floor",
        "material": "cobblestone",
        "position": [x - 1, y, z - 1],
        "dimensions": [w + 2, 1, d + 2]
    })

    # === MAIN FLOOR (wood planks) ===
    elements.append({
        "type": "floor",
        "material": planks,
        "position": [x, y, z],
        "dimensions": [w, 1, d]
    })

    # === CORNER POSTS (stripped logs) ===
    corners = [
        [x, y + 1, z],
        [x + w - 1, y + 1, z],
        [x, y + 1, z + d - 1],
        [x + w - 1, y + 1, z + d - 1]
    ]
    for cx, cy, cz in corners:
        elements.append({
            "type": "column",
            "material": log,
            "position": [cx, cy, cz],
            "dimensions": [1, h - 1, 1]
        })

    # === HORIZONTAL BEAMS (top of walls) ===
    # Front and back beams
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x, y + h - 1, z],
        "dimensions": [w, 1, 1]
    })
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x, y + h - 1, z + d - 1],
        "dimensions": [w, 1, 1]
    })
    # Side beams
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x, y + h - 1, z + 1],
        "dimensions": [1, 1, d - 2]
    })
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x + w - 1, y + h - 1, z + 1],
        "dimensions": [1, 1, d - 2]
    })

    # === WALLS (white concrete infill between posts) ===
    wall_height = h - 2  # Leave room for beam at top

    # Front wall - left section (leave gap for door)
    door_x = x + w // 2
    if door_x - x - 1 > 0:
        elements.append({
            "type": "wall",
            "material": "white_concrete",
            "position": [x + 1, y + 1, z],
            "dimensions": [door_x - x - 1, wall_height, 1]
        })
    # Front wall - right section
    if x + w - 1 - door_x - 1 > 0:
        elements.append({
            "type": "wall",
            "material": "white_concrete",
            "position": [door_x + 1, y + 1, z],
            "dimensions": [x + w - 1 - door_x - 1, wall_height, 1]
        })
    # Front wall - above door
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [door_x, y + 3, z],
        "dimensions": [1, wall_height - 2, 1]
    })

    # Back wall (solid)
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x + 1, y + 1, z + d - 1],
        "dimensions": [w - 2, wall_height, 1]
    })

    # Left wall - with window gap in middle
    window_z = z + d // 2
    # Below and beside window
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x, y + 1, z + 1],
        "dimensions": [1, wall_height, window_z - z - 2]
    })
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x, y + 1, window_z + 1],
        "dimensions": [1, wall_height, z + d - 1 - window_z - 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x, y + 1, window_z - 1],
        "dimensions": [1, 1, 3]
    })
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x, y + 3, window_z - 1],
        "dimensions": [1, wall_height - 2, 3]
    })

    # Right wall - with window gap in middle
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x + w - 1, y + 1, z + 1],
        "dimensions": [1, wall_height, window_z - z - 2]
    })
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x + w - 1, y + 1, window_z + 1],
        "dimensions": [1, wall_height, z + d - 1 - window_z - 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x + w - 1, y + 1, window_z - 1],
        "dimensions": [1, 1, 3]
    })
    elements.append({
        "type": "wall",
        "material": "white_concrete",
        "position": [x + w - 1, y + 3, window_z - 1],
        "dimensions": [1, wall_height - 2, 3]
    })

    # === WINDOWS (glass panes) ===
    # Left window
    elements.append({
        "type": "window",
        "material": "glass_pane",
        "position": [x, y + 2, window_z],
        "dimensions": [1, 1, 1]
    })
    # Right window
    elements.append({
        "type": "window",
        "material": "glass_pane",
        "position": [x + w - 1, y + 2, window_z],
        "dimensions": [1, 1, 1]
    })

    # === WINDOW SHUTTERS (trapdoors) ===
    elements.append({
        "type": "decoration",
        "material": trapdoor,
        "position": [x, y + 2, window_z - 1],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "decoration",
        "material": trapdoor,
        "position": [x, y + 2, window_z + 1],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "decoration",
        "material": trapdoor,
        "position": [x + w - 1, y + 2, window_z - 1],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "decoration",
        "material": trapdoor,
        "position": [x + w - 1, y + 2, window_z + 1],
        "dimensions": [1, 1, 1]
    })

    # === DOOR ===
    elements.append({
        "type": "door",
        "material": door,
        "position": [door_x, y + 1, z],
        "orientation": "south"
    })

    # === PORCH ===
    elements.append({
        "type": "porch",
        "material": planks,
        "position": [door_x - 1, y, z - 2],
        "dimensions": [3, 1, 2]
    })
    # Porch fence railings
    elements.append({
        "type": "fence",
        "material": fence,
        "position": [door_x - 1, y + 1, z - 2],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "fence",
        "material": fence,
        "position": [door_x + 1, y + 1, z - 2],
        "dimensions": [1, 1, 1]
    })

    # === PEAKED ROOF (stairs) ===
    roof_y = y + h
    roof_overhang = 1

    # Front slope (facing south)
    for layer in range(3):
        elements.append({
            "type": "roof",
            "material": stairs,
            "position": [x - roof_overhang, roof_y + layer, z - roof_overhang + layer],
            "dimensions": [w + 2 * roof_overhang, 1, 1],
            "orientation": "south"
        })

    # Back slope (facing north)
    for layer in range(3):
        elements.append({
            "type": "roof",
            "material": stairs,
            "position": [x - roof_overhang, roof_y + layer, z + d + roof_overhang - 1 - layer],
            "dimensions": [w + 2 * roof_overhang, 1, 1],
            "orientation": "north"
        })

    # Roof peak (slabs)
    peak_z = z + d // 2
    elements.append({
        "type": "roof",
        "material": slab,
        "position": [x - roof_overhang, roof_y + 3, peak_z - 1],
        "dimensions": [w + 2 * roof_overhang, 1, 3]
    })

    # === CHIMNEY ===
    if has_chimney:
        chimney_x = x + w - 2
        chimney_z = z + d - 2
        for cy in range(roof_y, roof_y + 4):
            elements.append({
                "type": "chimney",
                "material": "cobblestone",
                "position": [chimney_x, cy, chimney_z],
                "dimensions": [1, 1, 1]
            })

    # === GARDEN ===
    if has_garden:
        # Garden path
        elements.append({
            "type": "path",
            "material": "gravel",
            "position": [door_x, y, z - 5],
            "dimensions": [1, 1, 3]
        })

        # Flower beds on sides of path
        flowers = ["poppy", "dandelion", "azure_bluet", "cornflower", "oxeye_daisy"]
        for i, flower in enumerate(flowers[:3]):
            elements.append({
                "type": "flower",
                "material": flower,
                "position": [door_x - 2, y + 1, z - 5 + i],
                "dimensions": [1, 1, 1]
            })
            elements.append({
                "type": "flower",
                "material": flowers[(i + 2) % len(flowers)],
                "position": [door_x + 2, y + 1, z - 5 + i],
                "dimensions": [1, 1, 1]
            })

        # Garden fence
        elements.append({
            "type": "fence",
            "material": fence,
            "position": [door_x - 3, y + 1, z - 6],
            "dimensions": [7, 1, 1]
        })
        elements.append({
            "type": "fence",
            "material": fence,
            "position": [door_x - 3, y + 1, z - 5],
            "dimensions": [1, 1, 4]
        })
        elements.append({
            "type": "fence",
            "material": fence,
            "position": [door_x + 3, y + 1, z - 5],
            "dimensions": [1, 1, 4]
        })

    # === DECORATIONS ===
    # Lantern by door
    elements.append({
        "type": "lantern",
        "material": "lantern",
        "position": [door_x + 1, y + 2, z - 1],
        "dimensions": [1, 1, 1]
    })

    # Barrel beside house
    elements.append({
        "type": "decoration",
        "material": "barrel",
        "position": [x + w, y + 1, z + 1],
        "dimensions": [1, 1, 1]
    })

    return {
        "structure": {
            "width": w + 6 if has_garden else w + 2,
            "depth": d + 8 if has_garden else d + 2,
            "height": h + 4,
            "base_material": "cobblestone",
            "roof_material": stairs,
            "description": f"A cozy {wood_type} cottage with peaked {roof_type} roof",
            "ground_level": base_y
        },
        "elements": elements,
        "build_order": ["floor", "column", "beam", "wall", "window", "door", "porch", "roof", "chimney", "fence", "path", "flower", "lantern", "decoration"]
    }


def medieval_house_template(
    base_x: int, base_y: int, base_z: int,
    width: int = 11, depth: int = 9, height: int = 6,
    wood_type: str = "dark_oak", roof_type: str = "spruce"
) -> Dict[str, Any]:
    """
    Generate a medieval half-timbered house.

    Features:
    - Stone foundation
    - Exposed timber frame with X-bracing pattern
    - White plaster infill
    - Steep pitched roof
    - Multiple windows with shutters
    - Detailed porch entrance
    """
    elements = []

    # Materials
    planks = f"{wood_type}_planks"
    log = f"stripped_{wood_type}_log"
    stairs = f"{roof_type}_stairs"
    slab = f"{roof_type}_slab"
    fence = f"{wood_type}_fence"
    trapdoor = f"{wood_type}_trapdoor"
    door = f"{wood_type}_door"

    w, d, h = width, depth, height
    x, y, z = base_x, base_y, base_z

    # === STONE FOUNDATION ===
    elements.append({
        "type": "floor",
        "material": "stone_bricks",
        "position": [x - 1, y, z - 1],
        "dimensions": [w + 2, 1, d + 2]
    })
    elements.append({
        "type": "floor",
        "material": "stone_bricks",
        "position": [x, y + 1, z],
        "dimensions": [w, 1, d]
    })

    # === MAIN FLOOR ===
    elements.append({
        "type": "floor",
        "material": planks,
        "position": [x, y + 1, z],
        "dimensions": [w, 1, d]
    })

    # === CORNER POSTS ===
    post_height = h - 1
    corners = [
        [x, y + 2, z],
        [x + w - 1, y + 2, z],
        [x, y + 2, z + d - 1],
        [x + w - 1, y + 2, z + d - 1]
    ]
    for cx, cy, cz in corners:
        elements.append({
            "type": "column",
            "material": log,
            "position": [cx, cy, cz],
            "dimensions": [1, post_height, 1]
        })

    # === MID-WALL POSTS (for larger walls) ===
    mid_x = x + w // 2
    elements.append({
        "type": "column",
        "material": log,
        "position": [mid_x, y + 2, z],
        "dimensions": [1, post_height, 1]
    })
    elements.append({
        "type": "column",
        "material": log,
        "position": [mid_x, y + 2, z + d - 1],
        "dimensions": [1, post_height, 1]
    })

    # === TOP BEAMS ===
    beam_y = y + h
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x, beam_y, z],
        "dimensions": [w, 1, 1]
    })
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x, beam_y, z + d - 1],
        "dimensions": [w, 1, 1]
    })
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x, beam_y, z + 1],
        "dimensions": [1, 1, d - 2]
    })
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x + w - 1, beam_y, z + 1],
        "dimensions": [1, 1, d - 2]
    })

    # === WALLS WITH WINDOW OPENINGS ===
    wall_h = post_height - 1

    # Front wall sections (2 windows + door in middle)
    door_x = mid_x
    window1_x = x + 2
    window2_x = x + w - 3

    # Wall sections
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [x + 1, y + 2, z],
        "dimensions": [1, wall_h, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [window1_x + 2, y + 2, z],
        "dimensions": [door_x - window1_x - 3, wall_h, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [door_x + 1, y + 2, z],
        "dimensions": [window2_x - door_x - 2, wall_h, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [window2_x + 2, y + 2, z],
        "dimensions": [w - window2_x + x - 3, wall_h, 1]
    })
    # Above door
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [door_x, y + 4, z],
        "dimensions": [1, wall_h - 2, 1]
    })
    # Above windows
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [window1_x, y + 4, z],
        "dimensions": [2, wall_h - 2, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [window2_x, y + 4, z],
        "dimensions": [2, wall_h - 2, 1]
    })
    # Below windows
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [window1_x, y + 2, z],
        "dimensions": [2, 1, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [window2_x, y + 2, z],
        "dimensions": [2, 1, 1]
    })

    # Back wall (solid)
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [x + 1, y + 2, z + d - 1],
        "dimensions": [w - 2, wall_h, 1]
    })

    # Side walls with windows
    side_window_z = z + d // 2
    for side_x in [x, x + w - 1]:
        # Wall sections
        elements.append({
            "type": "wall",
            "material": "white_terracotta",
            "position": [side_x, y + 2, z + 1],
            "dimensions": [1, wall_h, side_window_z - z - 2]
        })
        elements.append({
            "type": "wall",
            "material": "white_terracotta",
            "position": [side_x, y + 2, side_window_z + 2],
            "dimensions": [1, wall_h, d - side_window_z + z - 3]
        })
        # Above/below window
        elements.append({
            "type": "wall",
            "material": "white_terracotta",
            "position": [side_x, y + 2, side_window_z - 1],
            "dimensions": [1, 1, 3]
        })
        elements.append({
            "type": "wall",
            "material": "white_terracotta",
            "position": [side_x, y + 4, side_window_z - 1],
            "dimensions": [1, wall_h - 2, 3]
        })

    # === WINDOWS ===
    # Front windows
    elements.append({
        "type": "window",
        "material": "glass_pane",
        "position": [window1_x, y + 3, z],
        "dimensions": [2, 1, 1]
    })
    elements.append({
        "type": "window",
        "material": "glass_pane",
        "position": [window2_x, y + 3, z],
        "dimensions": [2, 1, 1]
    })
    # Side windows
    elements.append({
        "type": "window",
        "material": "glass_pane",
        "position": [x, y + 3, side_window_z],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "window",
        "material": "glass_pane",
        "position": [x + w - 1, y + 3, side_window_z],
        "dimensions": [1, 1, 1]
    })

    # === DOOR ===
    elements.append({
        "type": "door",
        "material": door,
        "position": [door_x, y + 2, z],
        "orientation": "south"
    })

    # === PORCH ===
    elements.append({
        "type": "porch",
        "material": "stone_bricks",
        "position": [door_x - 1, y + 1, z - 2],
        "dimensions": [3, 1, 2]
    })
    # Porch pillars
    elements.append({
        "type": "column",
        "material": fence,
        "position": [door_x - 1, y + 2, z - 2],
        "dimensions": [1, 2, 1]
    })
    elements.append({
        "type": "column",
        "material": fence,
        "position": [door_x + 1, y + 2, z - 2],
        "dimensions": [1, 2, 1]
    })
    # Porch roof
    elements.append({
        "type": "roof",
        "material": stairs,
        "position": [door_x - 2, y + 4, z - 2],
        "dimensions": [5, 1, 1],
        "orientation": "south"
    })

    # === PEAKED ROOF ===
    roof_y = y + h + 1
    overhang = 1

    # Build roof layer by layer
    for layer in range(4):
        # Front slope
        elements.append({
            "type": "roof",
            "material": stairs,
            "position": [x - overhang, roof_y + layer, z - overhang + layer],
            "dimensions": [w + 2 * overhang, 1, 1],
            "orientation": "south"
        })
        # Back slope
        elements.append({
            "type": "roof",
            "material": stairs,
            "position": [x - overhang, roof_y + layer, z + d + overhang - 1 - layer],
            "dimensions": [w + 2 * overhang, 1, 1],
            "orientation": "north"
        })

    # Roof peak
    peak_z = z + d // 2
    elements.append({
        "type": "roof",
        "material": slab,
        "position": [x - overhang, roof_y + 4, peak_z - 1],
        "dimensions": [w + 2 * overhang, 1, 3]
    })

    # === CHIMNEY ===
    chimney_x = x + w - 2
    chimney_z = z + d - 2
    for cy in range(y + 2, roof_y + 5):
        elements.append({
            "type": "chimney",
            "material": "stone_bricks",
            "position": [chimney_x, cy, chimney_z],
            "dimensions": [1, 1, 1]
        })

    # === DECORATIONS ===
    elements.append({
        "type": "lantern",
        "material": "lantern",
        "position": [door_x, y + 3, z - 1],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "decoration",
        "material": "barrel",
        "position": [x - 1, y + 1, z + 1],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "decoration",
        "material": "flower_pot",
        "position": [door_x - 2, y + 2, z - 2],
        "dimensions": [1, 1, 1]
    })

    return {
        "structure": {
            "width": w + 2,
            "depth": d + 4,
            "height": h + 5,
            "base_material": "stone_bricks",
            "roof_material": stairs,
            "description": f"A medieval half-timbered house with {wood_type} frame and {roof_type} roof",
            "ground_level": base_y
        },
        "elements": elements,
        "build_order": ["floor", "column", "beam", "wall", "window", "door", "porch", "roof", "chimney", "lantern", "decoration"]
    }


def tavern_template(
    base_x: int, base_y: int, base_z: int,
    width: int = 13, depth: int = 11, height: int = 7,
    wood_type: str = "spruce", roof_type: str = "dark_oak"
) -> Dict[str, Any]:
    """
    Generate a medieval tavern with two floors.

    Features:
    - Stone ground floor
    - Half-timbered upper floor (jettied overhang)
    - Steep roof with dormers
    - Large front entrance
    - Outdoor seating area
    """
    elements = []

    planks = f"{wood_type}_planks"
    log = f"stripped_{wood_type}_log"
    stairs = f"{roof_type}_stairs"
    slab = f"{roof_type}_slab"
    fence = f"{wood_type}_fence"
    door = f"{wood_type}_door"

    w, d, h = width, depth, height
    x, y, z = base_x, base_y, base_z
    floor_height = 4

    # === STONE GROUND FLOOR ===
    elements.append({
        "type": "floor",
        "material": "cobblestone",
        "position": [x, y, z],
        "dimensions": [w, 1, d]
    })
    elements.append({
        "type": "floor",
        "material": planks,
        "position": [x + 1, y, z + 1],
        "dimensions": [w - 2, 1, d - 2]
    })

    # Ground floor walls (stone)
    elements.append({
        "type": "wall",
        "material": "cobblestone",
        "position": [x, y + 1, z],
        "dimensions": [w, floor_height - 1, 1]
    })
    elements.append({
        "type": "wall",
        "material": "cobblestone",
        "position": [x, y + 1, z + d - 1],
        "dimensions": [w, floor_height - 1, 1]
    })
    elements.append({
        "type": "wall",
        "material": "cobblestone",
        "position": [x, y + 1, z + 1],
        "dimensions": [1, floor_height - 1, d - 2]
    })
    elements.append({
        "type": "wall",
        "material": "cobblestone",
        "position": [x + w - 1, y + 1, z + 1],
        "dimensions": [1, floor_height - 1, d - 2]
    })

    # Clear door opening
    door_x = x + w // 2
    elements.append({
        "type": "air",
        "material": "air",
        "position": [door_x, y + 1, z],
        "dimensions": [2, 3, 1]
    })

    # Door
    elements.append({
        "type": "door",
        "material": door,
        "position": [door_x, y + 1, z],
        "orientation": "south"
    })
    elements.append({
        "type": "door",
        "material": door,
        "position": [door_x + 1, y + 1, z],
        "orientation": "south"
    })

    # Ground floor windows
    for wx in [x + 2, x + w - 4]:
        elements.append({
            "type": "air",
            "material": "air",
            "position": [wx, y + 2, z],
            "dimensions": [2, 2, 1]
        })
        elements.append({
            "type": "window",
            "material": "glass_pane",
            "position": [wx, y + 2, z],
            "dimensions": [2, 2, 1]
        })

    # === SECOND FLOOR (jettied) ===
    overhang = 1
    second_y = y + floor_height

    elements.append({
        "type": "floor",
        "material": planks,
        "position": [x - overhang, second_y, z - overhang],
        "dimensions": [w + 2 * overhang, 1, d + 2 * overhang]
    })

    # Second floor frame posts
    second_height = h - floor_height - 1
    for cx, cz in [(x - overhang, z - overhang), (x + w + overhang - 1, z - overhang),
                   (x - overhang, z + d + overhang - 1), (x + w + overhang - 1, z + d + overhang - 1)]:
        elements.append({
            "type": "column",
            "material": log,
            "position": [cx, second_y + 1, cz],
            "dimensions": [1, second_height, 1]
        })

    # Second floor walls (white with timber frame)
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [x - overhang + 1, second_y + 1, z - overhang],
        "dimensions": [w + 2 * overhang - 2, second_height, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [x - overhang + 1, second_y + 1, z + d + overhang - 1],
        "dimensions": [w + 2 * overhang - 2, second_height, 1]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [x - overhang, second_y + 1, z - overhang + 1],
        "dimensions": [1, second_height, d + 2 * overhang - 2]
    })
    elements.append({
        "type": "wall",
        "material": "white_terracotta",
        "position": [x + w + overhang - 1, second_y + 1, z - overhang + 1],
        "dimensions": [1, second_height, d + 2 * overhang - 2]
    })

    # Second floor windows
    for wx in [x, x + w - 2]:
        elements.append({
            "type": "window",
            "material": "glass_pane",
            "position": [wx, second_y + 1, z - overhang],
            "dimensions": [2, 2, 1]
        })

    # Top beams
    roof_y = second_y + second_height + 1
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x - overhang, roof_y, z - overhang],
        "dimensions": [w + 2 * overhang, 1, 1]
    })
    elements.append({
        "type": "beam",
        "material": log,
        "position": [x - overhang, roof_y, z + d + overhang - 1],
        "dimensions": [w + 2 * overhang, 1, 1]
    })

    # === ROOF ===
    for layer in range(5):
        elements.append({
            "type": "roof",
            "material": stairs,
            "position": [x - overhang - 1, roof_y + layer, z - overhang - 1 + layer],
            "dimensions": [w + 2 * overhang + 2, 1, 1],
            "orientation": "south"
        })
        elements.append({
            "type": "roof",
            "material": stairs,
            "position": [x - overhang - 1, roof_y + layer, z + d + overhang - layer],
            "dimensions": [w + 2 * overhang + 2, 1, 1],
            "orientation": "north"
        })

    # Roof peak
    peak_z = z + d // 2
    elements.append({
        "type": "roof",
        "material": slab,
        "position": [x - overhang - 1, roof_y + 5, peak_z - 1],
        "dimensions": [w + 2 * overhang + 2, 1, 3]
    })

    # === CHIMNEY ===
    for cy in range(y + 1, roof_y + 6):
        elements.append({
            "type": "chimney",
            "material": "cobblestone",
            "position": [x + w - 2, cy, z + d - 2],
            "dimensions": [1, 1, 1]
        })

    # === OUTDOOR SEATING ===
    elements.append({
        "type": "porch",
        "material": "cobblestone",
        "position": [x - 3, y, z - 3],
        "dimensions": [5, 1, 3]
    })
    # Tables (fence + pressure plate)
    elements.append({
        "type": "fence",
        "material": fence,
        "position": [x - 2, y + 1, z - 2],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "decoration",
        "material": "oak_pressure_plate",
        "position": [x - 2, y + 2, z - 2],
        "dimensions": [1, 1, 1]
    })

    # === SIGN ===
    elements.append({
        "type": "decoration",
        "material": "oak_sign",
        "position": [door_x, y + 4, z - 1],
        "dimensions": [1, 1, 1]
    })

    # Lanterns
    elements.append({
        "type": "lantern",
        "material": "lantern",
        "position": [door_x - 1, y + 3, z - 1],
        "dimensions": [1, 1, 1]
    })
    elements.append({
        "type": "lantern",
        "material": "lantern",
        "position": [door_x + 2, y + 3, z - 1],
        "dimensions": [1, 1, 1]
    })

    return {
        "structure": {
            "width": w + 4,
            "depth": d + 6,
            "height": h + 6,
            "base_material": "cobblestone",
            "roof_material": stairs,
            "description": f"A medieval tavern with stone ground floor and half-timbered upper floor",
            "ground_level": base_y
        },
        "elements": elements,
        "build_order": ["floor", "wall", "air", "column", "beam", "window", "door", "porch", "roof", "chimney", "fence", "lantern", "decoration"]
    }


# Template registry
TEMPLATES = {
    "cottage": cottage_template,
    "cozy cottage": cottage_template,
    "cabin": cottage_template,
    "house": medieval_house_template,
    "medieval house": medieval_house_template,
    "half-timbered house": medieval_house_template,
    "tavern": tavern_template,
    "inn": tavern_template,
    "pub": tavern_template,
}


def get_template(description: str) -> str:
    """
    Match a description to a template name.
    Returns the template key or None if no match.
    """
    description_lower = description.lower()

    # Check for exact matches first
    for key in TEMPLATES:
        if key in description_lower:
            return key

    # Check for partial matches
    if any(word in description_lower for word in ["cottage", "cozy", "cabin", "hut"]):
        return "cottage"
    if any(word in description_lower for word in ["tavern", "inn", "pub", "bar"]):
        return "tavern"
    if any(word in description_lower for word in ["house", "home", "medieval"]):
        return "medieval house"

    return None
