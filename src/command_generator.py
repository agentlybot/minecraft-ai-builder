"""
Command Generator - Blueprint to Minecraft Commands

Converts spatial blueprints into executable Minecraft commands.
Optimizes for:
- Command batching
- Performance (using /fill for large areas)
- Syntax validity
- Architectural correctness (door accessibility, structural connections)
"""

from typing import List, Dict, Any, Tuple, Optional


class CommandGenerator:
    """Convert spatial blueprints to Minecraft commands"""

    def __init__(self):
        """Initialize command generator"""
        self.commands = []
        self.ground_level = -60  # Default for superflat, updated from blueprint
        self.structure_bounds = {}  # Track structure boundaries for door orientation
        self.doors = []  # Track door positions for accessibility check
        self.floors = []  # Track floor positions

    def generate(self, blueprint: Dict[str, Any]) -> List[str]:
        """
        Generate Minecraft commands from a blueprint.

        Args:
            blueprint: Spatial blueprint (from SpatialAnalyzer)

        Returns:
            List of Minecraft commands ready to execute
        """
        self.commands = []
        self.doors = []
        self.floors = []

        # Check if this is a voxel blueprint (direct block placement)
        if blueprint.get("is_voxel"):
            return self._generate_voxel_commands(blueprint)

        # Extract structure info
        structure = blueprint.get("structure", {})
        elements = blueprint.get("elements", [])

        # Get ground level from structure or use default
        self.ground_level = structure.get("ground_level", -60)

        # Calculate structure bounds for door orientation validation
        self._calculate_structure_bounds(elements)

        # Build order
        build_order = blueprint.get("build_order", [])

        # Generate commands for each build step
        for step in build_order:
            step_elements = [e for e in elements if e.get("type") == step]
            for element in step_elements:
                self._generate_element_commands(element, structure)

        # Post-processing: ensure door accessibility
        self._ensure_door_accessibility()

        return self.commands

    def _generate_voxel_commands(self, blueprint: Dict[str, Any]) -> List[str]:
        """
        Generate commands from a voxel-based blueprint.
        Each element is a single block with exact position.
        """
        elements = blueprint.get("elements", [])
        commands = []

        for element in elements:
            material = element.get("material", "")
            pos = element.get("position", [0, 0, 0])

            if not material or material == "":
                continue

            x, y, z = pos[0], pos[1], pos[2]

            if material == "air":
                commands.append(f"setblock {x} {y} {z} air")
            else:
                # Handle special blocks with states
                block_state = self._get_block_state(material, element)
                commands.append(f"setblock {x} {y} {z} {material}{block_state}")

        return commands

    def _get_block_state(self, material: str, element: Dict[str, Any]) -> str:
        """Get block state string for special blocks."""
        # Stairs need facing direction
        if "stairs" in material:
            # Default facing based on position in structure
            # For now, use a simple heuristic
            return ""  # Minecraft will use default facing

        # Doors need facing and half
        if "door" in material:
            return "[half=lower]"

        # Slabs
        if "slab" in material:
            return "[type=bottom]"

        return ""

    def _calculate_structure_bounds(self, elements: List[Dict]) -> None:
        """Calculate the bounding box of the structure for door orientation."""
        min_x, max_x = float('inf'), float('-inf')
        min_z, max_z = float('inf'), float('-inf')

        for elem in elements:
            pos = elem.get("position", [0, 0, 0])
            dims = elem.get("dimensions", [1, 1, 1])
            if pos and dims:
                min_x = min(min_x, pos[0])
                max_x = max(max_x, pos[0] + dims[0])
                min_z = min(min_z, pos[2])
                max_z = max(max_z, pos[2] + dims[2])

        self.structure_bounds = {
            "min_x": min_x, "max_x": max_x,
            "min_z": min_z, "max_z": max_z,
            "center_x": (min_x + max_x) / 2,
            "center_z": (min_z + max_z) / 2
        }

    def _ensure_door_accessibility(self) -> None:
        """
        Post-process to ensure all doors are accessible.
        Adds stairs if doors are elevated above ground level.
        """
        for door in self.doors:
            door_x, door_y, door_z = door["position"]
            orientation = door.get("orientation", "south")

            # Check if door is at ground level
            expected_door_y = self.ground_level + 1

            if door_y > expected_door_y:
                # Door is elevated - add stairs leading up to it
                height_diff = door_y - expected_door_y
                self._add_stairs_to_door(door_x, door_y, door_z, orientation, height_diff)

    def _add_stairs_to_door(self, door_x: int, door_y: int, door_z: int,
                            orientation: str, height: int) -> None:
        """
        Add stairs leading up to an elevated door.
        Stairs are placed INSIDE the building (opposite side of door orientation).
        Door faces outward, stairs approach from inside.
        """
        stair_material = "oak_stairs"

        # Stairs go INSIDE (opposite of door facing direction)
        # If door faces south (opens outward), stairs approach from north (inside)
        for i in range(height):
            stair_y = self.ground_level + 1 + i

            if orientation == "south":
                # Door faces south, stairs inside going north->south
                stair_z = door_z - (height - 1 - i)  # Start inside, end at door
                facing = "south"
                self.commands.append(f"/setblock {door_x} {stair_y} {stair_z} {stair_material}[facing={facing}]")
            elif orientation == "north":
                # Door faces north, stairs inside going south->north
                stair_z = door_z + (height - 1 - i)
                facing = "north"
                self.commands.append(f"/setblock {door_x} {stair_y} {stair_z} {stair_material}[facing={facing}]")
            elif orientation == "east":
                # Door faces east, stairs inside going west->east
                stair_x = door_x - (height - 1 - i)
                facing = "east"
                self.commands.append(f"/setblock {stair_x} {stair_y} {door_z} {stair_material}[facing={facing}]")
            elif orientation == "west":
                # Door faces west, stairs inside going east->west
                stair_x = door_x + (height - 1 - i)
                facing = "west"
                self.commands.append(f"/setblock {stair_x} {stair_y} {door_z} {stair_material}[facing={facing}]")

    def _get_interior_facing_orientation(self, x: int, z: int) -> str:
        """
        Determine which direction a door should face to open toward the interior.
        Based on position relative to structure center.
        """
        if not self.structure_bounds:
            return "south"

        center_x = self.structure_bounds["center_x"]
        center_z = self.structure_bounds["center_z"]

        dx = center_x - x
        dz = center_z - z

        # Door should face toward the center (interior)
        if abs(dx) > abs(dz):
            return "east" if dx > 0 else "west"
        else:
            return "south" if dz > 0 else "north"
    
    def _generate_element_commands(self, element: Dict[str, Any], structure: Dict[str, Any]) -> None:
        """Generate commands for a single element"""

        elem_type = element.get("type")
        material = element.get("material", "stone")

        if elem_type == "wall":
            self._generate_fill(element, material)
        elif elem_type == "floor":
            self._generate_fill(element, material)
            # Track floor for door accessibility checks
            self.floors.append(element)
        elif elem_type == "door":
            self._generate_door(element, material)
        elif elem_type == "window":
            # Windows are arrays of positions
            positions = element.get("position", [])
            if isinstance(positions, list) and len(positions) > 0:
                if isinstance(positions[0], (list, tuple)):
                    # Multiple positions
                    for pos in positions:
                        self._generate_setblock_at(pos, material)
                else:
                    # Single position
                    self._generate_setblock(element, material)
        elif elem_type == "roof":
            self._generate_roof(element, material)
        elif elem_type == "stairs":
            self._generate_stairs(element, material)
        elif elem_type == "decoration":
            self._generate_setblock(element, material)
        elif elem_type == "bridge":
            self._generate_bridge(element, material)
        elif elem_type == "tower":
            self._generate_tower(element, material, structure)
        elif elem_type == "chain":
            self._generate_chain(element)
        elif elem_type == "garden":
            self._generate_garden(element, material)
        elif elem_type == "fence":
            self._generate_fence(element, material)
        elif elem_type == "path":
            self._generate_path(element, material)
        elif elem_type == "lantern":
            self._generate_setblock(element, material)
        elif elem_type == "chimney":
            self._generate_chimney(element, material)
        elif elem_type == "flower":
            self._generate_flower(element, material)
        elif elem_type == "water":
            self._generate_water(element)
        elif elem_type == "pond":
            self._generate_pond(element)
        elif elem_type == "fountain":
            self._generate_fountain(element)
        elif elem_type == "well":
            self._generate_well(element)
        elif elem_type == "crops":
            self._generate_crops(element, material)
        elif elem_type == "farm":
            self._generate_farm(element, material)
        elif elem_type == "tree":
            self._generate_tree(element, material)
        elif elem_type == "torch":
            self._generate_setblock(element, "torch")
        elif elem_type == "lamp":
            self._generate_setblock(element, material or "lantern")
        elif elem_type == "bed":
            self._generate_bed(element, material)
        elif elem_type == "chest":
            self._generate_setblock(element, "chest")
        elif elem_type == "barrel":
            self._generate_setblock(element, "barrel")
        elif elem_type == "crafting_table":
            self._generate_setblock(element, "crafting_table")
        elif elem_type == "furnace":
            self._generate_setblock(element, "furnace")
        elif elem_type == "anvil":
            self._generate_setblock(element, "anvil")
        elif elem_type == "bookshelf":
            self._generate_fill(element, "bookshelf")
        elif elem_type == "carpet":
            self._generate_fill(element, material or "red_carpet")
        elif elem_type == "ladder":
            self._generate_ladder(element)
        elif elem_type == "trapdoor":
            self._generate_setblock(element, material or "oak_trapdoor")
        elif elem_type == "table":
            self._generate_table(element)
        elif elem_type == "chair":
            self._generate_chair(element, material)
        elif elem_type == "fireplace":
            self._generate_fireplace(element)
        elif elem_type == "column":
            self._generate_column(element, material)
        elif elem_type == "pillar":
            self._generate_column(element, material)
        elif elem_type == "arch":
            self._generate_arch(element, material)
        elif elem_type == "balcony":
            self._generate_balcony(element, material)
        elif elem_type == "porch":
            self._generate_porch(element, material)
        elif elem_type == "awning":
            self._generate_awning(element, material)
        elif elem_type == "market_stall":
            self._generate_market_stall(element, material)
        elif elem_type == "stall":
            self._generate_market_stall(element, material)
        elif elem_type == "stable":
            self._generate_stable(element, material)
        elif elem_type == "pen":
            self._generate_pen(element, material)
        elif elem_type == "dock":
            self._generate_dock(element, material)
        elif elem_type == "platform":
            self._generate_fill(element, material)
        elif elem_type == "banner":
            self._generate_banner(element, material)
        elif elem_type == "sign":
            self._generate_sign(element)
        elif elem_type == "painting":
            self._generate_setblock(element, "painting")
        elif elem_type == "bell":
            self._generate_setblock(element, "bell")
        elif elem_type == "hay":
            self._generate_fill(element, "hay_block")
        elif elem_type == "log_pile":
            self._generate_fill(element, material or "oak_log")
        elif elem_type == "crate":
            self._generate_fill(element, "barrel")
        elif elem_type == "slab":
            self._generate_fill(element, material)
        elif elem_type == "beam":
            self._generate_fill(element, material or "oak_log")
        elif elem_type == "support":
            self._generate_column(element, material or "oak_fence")
        elif elem_type == "railing":
            self._generate_fence(element, material or "oak_fence")
        elif elem_type == "moat":
            self._generate_moat(element)
        elif elem_type == "drawbridge":
            self._generate_bridge(element, material or "oak_planks")
        elif elem_type == "gate":
            self._generate_gate(element, material)
        elif elem_type == "portcullis":
            self._generate_portcullis(element)
        elif elem_type == "battlement":
            self._generate_battlement(element, material)
        elif elem_type == "crenellation":
            self._generate_battlement(element, material)
        elif elem_type == "arrow_slit":
            self._generate_arrow_slit(element)
        elif elem_type == "throne":
            self._generate_throne(element)
        elif elem_type == "altar":
            self._generate_altar(element)
        elif elem_type == "statue":
            self._generate_statue(element, material)
        elif elem_type == "obelisk":
            self._generate_obelisk(element, material)
        elif elem_type == "pyramid":
            self._generate_pyramid(element, material)
        elif elem_type == "dome":
            self._generate_dome(element, material)
        elif elem_type == "spire":
            self._generate_spire(element, material)
        elif elem_type == "windmill":
            self._generate_windmill(element)

    def _generate_door(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate door with proper orientation and accessibility tracking.
        Doors are 2 blocks tall (lower and upper half).
        """
        position = element.get("position")
        if not position:
            return

        x, y, z = position
        orientation = element.get("orientation")

        # If no orientation specified, calculate interior-facing orientation
        if not orientation:
            orientation = self._get_interior_facing_orientation(x, z)

        # Track door for accessibility post-processing
        self.doors.append({
            "position": [x, y, z],
            "orientation": orientation,
            "accessible_from": element.get("accessible_from", "interior")
        })

        # Generate lower and upper door halves
        self.commands.append(f"/setblock {x} {y} {z} {material}[facing={orientation},half=lower]")
        self.commands.append(f"/setblock {x} {y+1} {z} {material}[facing={orientation},half=upper]")

    def _generate_stairs(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate stairs that stay WITHIN the building footprint.
        Uses a spiral pattern for tall structures or L-shaped for shorter ones.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 4, 3])  # Default 3x3 footprint

        if not position:
            return

        x, y, z = position
        width, height, depth = dimensions

        # Stairs must fit within the given footprint
        # Use spiral staircase pattern that stays inside

        if height <= 4:
            # Simple straight stairs along one wall (inside the building)
            for i in range(height):
                stair_y = y + i
                stair_z = z + min(i, depth - 1)  # Stay within depth
                self.commands.append(f"/setblock {x} {stair_y} {stair_z} {material}[facing=north]")
        else:
            # Spiral staircase - rotates around the interior
            # Pattern: south wall -> east wall -> north wall -> west wall -> repeat
            directions = [
                ("south", 0, 1, "north"),   # Move +z, face north
                ("east", 1, 0, "west"),     # Move +x, face west
                ("north", 0, -1, "south"),  # Move -z, face south
                ("west", -1, 0, "east")     # Move -x, face east
            ]

            # Start position (inside corner)
            curr_x, curr_z = x + 1, z + 1
            max_x, max_z = x + width - 2, z + depth - 2
            min_x, min_z = x + 1, z + 1

            dir_idx = 0
            steps_in_dir = 0
            side_length = min(width, depth) - 2  # Inner dimension

            for i in range(height):
                stair_y = y + i

                # Place stair block
                _, dx, dz, facing = directions[dir_idx % 4]
                self.commands.append(f"/setblock {curr_x} {stair_y} {curr_z} {material}[facing={facing}]")

                # Move to next position (staying inside)
                next_x = curr_x + dx
                next_z = curr_z + dz

                # Check bounds and change direction if needed
                steps_in_dir += 1
                if steps_in_dir >= side_length - 1 or \
                   next_x < min_x or next_x > max_x or \
                   next_z < min_z or next_z > max_z:
                    dir_idx += 1
                    steps_in_dir = 0
                    _, dx, dz, _ = directions[dir_idx % 4]
                    next_x = curr_x + dx
                    next_z = curr_z + dz

                # Clamp to bounds
                curr_x = max(min_x, min(max_x, next_x))
                curr_z = max(min_z, min(max_z, next_z))

    def _generate_bridge(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate a bridge with deck and railings.
        Ensures both ends are anchored.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 1, 5])
        orientation = element.get("orientation", "south")

        if not position:
            return

        x, y, z = position
        width, height, length = dimensions

        # Bridge deck
        if orientation in ["south", "north"]:
            self.commands.append(f"/fill {x} {y} {z} {x+width-1} {y} {z+length-1} {material}")
            # Railings on sides
            self.commands.append(f"/fill {x} {y+1} {z} {x} {y+1} {z+length-1} oak_fence")
            self.commands.append(f"/fill {x+width-1} {y+1} {z} {x+width-1} {y+1} {z+length-1} oak_fence")
        else:
            self.commands.append(f"/fill {x} {y} {z} {x+length-1} {y} {z+width-1} {material}")
            # Railings on sides
            self.commands.append(f"/fill {x} {y+1} {z} {x+length-1} {y+1} {z} oak_fence")
            self.commands.append(f"/fill {x} {y+1} {z+width-1} {x+length-1} {y+1} {z+width-1} oak_fence")

    def _generate_chain(self, element: Dict[str, Any]) -> None:
        """
        Generate a chain connecting two points.
        Chains must be anchored at both ends.
        """
        position = element.get("position")  # Start position
        end_position = element.get("end_position")  # End position

        if not position or not end_position:
            return

        x1, y1, z1 = position
        x2, y2, z2 = end_position

        # Simple vertical or diagonal chain
        # Calculate steps
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        steps = max(abs(dx), abs(dy), abs(dz), 1)

        for i in range(steps + 1):
            cx = int(x1 + (dx * i / steps))
            cy = int(y1 + (dy * i / steps))
            cz = int(z1 + (dz * i / steps))
            self.commands.append(f"/setblock {cx} {cy} {cz} chain")

    def _generate_tower(self, element: Dict[str, Any], material: str, structure: Dict[str, Any]) -> None:
        """
        Generate a tower with walls and interior-facing door.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 10, 5])

        if not position:
            return

        x, y, z = position
        width, height, depth = dimensions

        # Tower walls (hollow)
        self.commands.append(f"/fill {x} {y} {z} {x+width-1} {y+height-1} {z+depth-1} {material} hollow")

        # Determine which side faces the interior (courtyard)
        interior_orientation = self._get_interior_facing_orientation(x + width//2, z + depth//2)

        # Place door on interior-facing wall
        door_x, door_z = x + width//2, z + depth//2
        if interior_orientation == "south":
            door_z = z + depth - 1
        elif interior_orientation == "north":
            door_z = z
        elif interior_orientation == "east":
            door_x = x + width - 1
        elif interior_orientation == "west":
            door_x = x

        # Clear door space and place door
        self.commands.append(f"/setblock {door_x} {y} {door_z} air")
        self.commands.append(f"/setblock {door_x} {y+1} {door_z} air")
        self.commands.append(f"/setblock {door_x} {y} {door_z} oak_door[facing={interior_orientation},half=lower]")
        self.commands.append(f"/setblock {door_x} {y+1} {door_z} oak_door[facing={interior_orientation},half=upper]")
    
    def _generate_fill(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate /fill command for large areas.
        
        /fill <x1> <y1> <z1> <x2> <y2> <z2> <block>
        """
        position = element.get("position", [0, 0, 0])
        dimensions = element.get("dimensions", [1, 1, 1])
        
        x1, y1, z1 = position
        width, height, depth = dimensions
        x2 = x1 + width - 1
        y2 = y1 + height - 1
        z2 = z1 + depth - 1
        
        cmd = f"/fill {x1} {y1} {z1} {x2} {y2} {z2} {material}"
        self.commands.append(cmd)
    
    def _generate_setblock(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate /setblock command for precise placement.
        
        /setblock <x> <y> <z> <block>
        """
        position = element.get("position")
        if not position:
            return
        
        x, y, z = position
        
        # Handle block properties (e.g., door orientation)
        orientation = element.get("orientation")
        if orientation == "north":
            cmd = f"/setblock {x} {y} {z} {material}[facing=north]"
        elif orientation == "south":
            cmd = f"/setblock {x} {y} {z} {material}[facing=south]"
        elif orientation == "east":
            cmd = f"/setblock {x} {y} {z} {material}[facing=east]"
        elif orientation == "west":
            cmd = f"/setblock {x} {y} {z} {material}[facing=west]"
        else:
            cmd = f"/setblock {x} {y} {z} {material}"
        
        self.commands.append(cmd)
    
    def _generate_setblock_at(self, position: List[int], material: str) -> None:
        """Generate setblock at a specific position"""
        x, y, z = position
        cmd = f"/setblock {x} {y} {z} {material}"
        self.commands.append(cmd)

    def _generate_garden(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate a garden area with flowers, grass, and optional water.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 1, 5])

        if not position:
            return

        x, y, z = position
        width, _, depth = dimensions

        # Lay grass base
        self.commands.append(f"/fill {x} {y} {z} {x+width-1} {y} {z+depth-1} grass_block")

        # Add scattered flowers on top of grass (y+1)
        flowers = ["poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower"]
        flower_idx = 0
        for fx in range(x + 1, x + width - 1, 2):
            for fz in range(z + 1, z + depth - 1, 2):
                flower = flowers[flower_idx % len(flowers)]
                self.commands.append(f"/setblock {fx} {y+1} {fz} {flower}")
                flower_idx += 1

    def _generate_fence(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate fence around an area.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 1, 5])

        if not position:
            return

        x, y, z = position
        width, height, depth = dimensions

        # Fence perimeter
        # North and south sides
        self.commands.append(f"/fill {x} {y} {z} {x+width-1} {y+height-1} {z} {material}")
        self.commands.append(f"/fill {x} {y} {z+depth-1} {x+width-1} {y+height-1} {z+depth-1} {material}")
        # East and west sides
        self.commands.append(f"/fill {x} {y} {z} {x} {y+height-1} {z+depth-1} {material}")
        self.commands.append(f"/fill {x+width-1} {y} {z} {x+width-1} {y+height-1} {z+depth-1} {material}")

    def _generate_path(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate a path (grass_path, gravel, etc).
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 1, 5])
        orientation = element.get("orientation", "south")

        if not position:
            return

        x, y, z = position
        width, _, length = dimensions

        # Path material defaults to grass_path
        path_material = material if material != "stone" else "dirt_path"

        if orientation in ["south", "north"]:
            self.commands.append(f"/fill {x} {y} {z} {x+width-1} {y} {z+length-1} {path_material}")
        else:
            self.commands.append(f"/fill {x} {y} {z} {x+length-1} {y} {z+width-1} {path_material}")

    def _generate_roof(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate roof section. If material contains 'stairs', place as stairs with orientation.
        Otherwise use fill for slabs/blocks.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 1, 5])
        orientation = element.get("orientation", "south")

        if not position:
            return

        x, y, z = position
        w, h, d = dimensions

        if "stairs" in material:
            # Place stairs row by row with proper facing
            facing_map = {
                "north": "south",  # stairs face opposite direction they slope toward
                "south": "north",
                "east": "west",
                "west": "east"
            }
            facing = facing_map.get(orientation, "north")

            if orientation in ["north", "south"]:
                # Stairs run along X axis
                for dx in range(w):
                    self.commands.append(f"/setblock {x+dx} {y} {z} {material}[facing={facing}]")
            else:
                # Stairs run along Z axis
                for dz in range(d):
                    self.commands.append(f"/setblock {x} {y} {z+dz} {material}[facing={facing}]")
        else:
            # Regular fill for slabs or blocks
            self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y+h-1} {z+d-1} {material}")

    def _generate_chimney(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate a chimney stack.
        """
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 3, 1])

        if not position:
            return

        x, y, z = position
        _, height, _ = dimensions

        # Chimney material defaults to cobblestone
        chimney_material = material if material != "stone" else "cobblestone"

        # Stack of blocks
        self.commands.append(f"/fill {x} {y} {z} {x} {y+height-1} {z} {chimney_material}")

        # Optional: add campfire/smoke at top
        self.commands.append(f"/setblock {x} {y+height} {z} campfire")

    def _generate_flower(self, element: Dict[str, Any], material: str) -> None:
        """
        Generate a flower. Flowers must be placed ON TOP of a solid block.
        """
        position = element.get("position")

        if not position:
            return

        x, y, z = position

        # Ensure there's a grass block below the flower
        self.commands.append(f"/setblock {x} {y-1} {z} grass_block")
        # Place the flower
        self.commands.append(f"/setblock {x} {y} {z} {material}")

    def _generate_water(self, element: Dict[str, Any]) -> None:
        """Generate water source blocks."""
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 1, 1])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y+h-1} {z+d-1} water")

    def _generate_pond(self, element: Dict[str, Any]) -> None:
        """Generate a natural-looking pond with sloped edges."""
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 2, 5])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        # Dig the hole
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} water")
        self.commands.append(f"/fill {x+1} {y-1} {z+1} {x+w-2} {y-1} {z+d-2} water")
        # Add lily pads on surface
        self.commands.append(f"/setblock {x+w//2} {y+1} {z+d//2} lily_pad")

    def _generate_fountain(self, element: Dict[str, Any]) -> None:
        """Generate a decorative fountain."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Base pool
        self.commands.append(f"/fill {x-1} {y} {z-1} {x+1} {y} {z+1} water")
        self.commands.append(f"/fill {x-2} {y-1} {z-2} {x+2} {y-1} {z+2} stone_bricks")
        # Center pillar
        self.commands.append(f"/fill {x} {y} {z} {x} {y+2} {z} stone_brick_wall")
        # Water on top
        self.commands.append(f"/setblock {x} {y+3} {z} water")

    def _generate_well(self, element: Dict[str, Any]) -> None:
        """Generate a village-style well."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Stone base
        self.commands.append(f"/fill {x-1} {y} {z-1} {x+1} {y+1} {z+1} cobblestone hollow")
        # Water inside
        self.commands.append(f"/fill {x} {y-2} {z} {x} {y} {z} water")
        # Roof posts
        self.commands.append(f"/fill {x-1} {y+2} {z-1} {x-1} {y+3} {z-1} oak_fence")
        self.commands.append(f"/fill {x+1} {y+2} {z-1} {x+1} {y+3} {z-1} oak_fence")
        self.commands.append(f"/fill {x-1} {y+2} {z+1} {x-1} {y+3} {z+1} oak_fence")
        self.commands.append(f"/fill {x+1} {y+2} {z+1} {x+1} {y+3} {z+1} oak_fence")
        # Roof
        self.commands.append(f"/fill {x-1} {y+4} {z-1} {x+1} {y+4} {z+1} oak_slab")

    def _generate_crops(self, element: Dict[str, Any], material: str) -> None:
        """Generate farmland with crops."""
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 1, 3])
        if not position:
            return
        x, y, z = position
        w, _, d = dimensions
        crop = material if material in ["wheat", "carrots", "potatoes", "beetroots"] else "wheat"
        # Farmland
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} farmland")
        # Crops on top
        self.commands.append(f"/fill {x} {y+1} {z} {x+w-1} {y+1} {z+d-1} {crop}")

    def _generate_farm(self, element: Dict[str, Any], material: str) -> None:
        """Generate a complete small farm with water irrigation."""
        position = element.get("position")
        dimensions = element.get("dimensions", [9, 1, 9])
        if not position:
            return
        x, y, z = position
        w, _, d = dimensions
        # Farmland with water channel in middle
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} farmland")
        self.commands.append(f"/fill {x+w//2} {y} {z} {x+w//2} {y} {z+d-1} water")
        # Crops
        self.commands.append(f"/fill {x} {y+1} {z} {x+w//2-1} {y+1} {z+d-1} wheat")
        self.commands.append(f"/fill {x+w//2+1} {y+1} {z} {x+w-1} {y+1} {z+d-1} carrots")

    def _generate_tree(self, element: Dict[str, Any], material: str) -> None:
        """Generate a simple tree."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        tree_type = material if material in ["oak", "birch", "spruce", "dark_oak", "jungle", "acacia"] else "oak"
        # Trunk
        self.commands.append(f"/fill {x} {y} {z} {x} {y+4} {z} {tree_type}_log")
        # Leaves
        self.commands.append(f"/fill {x-2} {y+3} {z-2} {x+2} {y+5} {z+2} {tree_type}_leaves replace air")
        self.commands.append(f"/fill {x-1} {y+6} {z-1} {x+1} {y+6} {z+1} {tree_type}_leaves replace air")

    def _generate_bed(self, element: Dict[str, Any], material: str) -> None:
        """Generate a bed (2 blocks)."""
        position = element.get("position")
        orientation = element.get("orientation", "south")
        if not position:
            return
        x, y, z = position
        color = material if material in ["red", "blue", "white", "green", "yellow"] else "red"
        if orientation in ["south", "north"]:
            self.commands.append(f"/setblock {x} {y} {z} {color}_bed[part=foot,facing={orientation}]")
        else:
            self.commands.append(f"/setblock {x} {y} {z} {color}_bed[part=foot,facing={orientation}]")

    def _generate_ladder(self, element: Dict[str, Any]) -> None:
        """Generate a ladder going up."""
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 4, 1])
        orientation = element.get("orientation", "south")
        if not position:
            return
        x, y, z = position
        _, height, _ = dimensions
        for i in range(height):
            self.commands.append(f"/setblock {x} {y+i} {z} ladder[facing={orientation}]")

    def _generate_table(self, element: Dict[str, Any]) -> None:
        """Generate a table (fence post + pressure plate)."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        self.commands.append(f"/setblock {x} {y} {z} oak_fence")
        self.commands.append(f"/setblock {x} {y+1} {z} oak_pressure_plate")

    def _generate_chair(self, element: Dict[str, Any], material: str) -> None:
        """Generate a chair (stairs block)."""
        position = element.get("position")
        orientation = element.get("orientation", "south")
        if not position:
            return
        x, y, z = position
        stair_type = material if "stairs" in material else "oak_stairs"
        self.commands.append(f"/setblock {x} {y} {z} {stair_type}[facing={orientation}]")

    def _generate_fireplace(self, element: Dict[str, Any]) -> None:
        """Generate a cozy fireplace."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Back wall
        self.commands.append(f"/fill {x-1} {y} {z} {x+1} {y+2} {z} stone_bricks")
        # Sides
        self.commands.append(f"/setblock {x-1} {y} {z+1} stone_bricks")
        self.commands.append(f"/setblock {x+1} {y} {z+1} stone_bricks")
        # Fire
        self.commands.append(f"/setblock {x} {y} {z+1} campfire")
        # Chimney start
        self.commands.append(f"/setblock {x} {y+3} {z} stone_bricks")

    def _generate_column(self, element: Dict[str, Any], material: str) -> None:
        """Generate a vertical column/pillar."""
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 4, 1])
        if not position:
            return
        x, y, z = position
        _, height, _ = dimensions
        self.commands.append(f"/fill {x} {y} {z} {x} {y+height-1} {z} {material}")

    def _generate_arch(self, element: Dict[str, Any], material: str) -> None:
        """Generate an arch/doorway."""
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 4, 1])
        if not position:
            return
        x, y, z = position
        w, h, _ = dimensions
        # Side columns
        self.commands.append(f"/fill {x} {y} {z} {x} {y+h-1} {z} {material}")
        self.commands.append(f"/fill {x+w-1} {y} {z} {x+w-1} {y+h-1} {z} {material}")
        # Top
        self.commands.append(f"/fill {x} {y+h-1} {z} {x+w-1} {y+h-1} {z} {material}")

    def _generate_balcony(self, element: Dict[str, Any], material: str) -> None:
        """Generate a balcony with railing."""
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 1, 3])
        if not position:
            return
        x, y, z = position
        w, _, d = dimensions
        # Floor
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} {material}")
        # Railing
        self.commands.append(f"/fill {x} {y+1} {z+d-1} {x+w-1} {y+1} {z+d-1} oak_fence")
        self.commands.append(f"/fill {x} {y+1} {z} {x} {y+1} {z+d-1} oak_fence")
        self.commands.append(f"/fill {x+w-1} {y+1} {z} {x+w-1} {y+1} {z+d-1} oak_fence")

    def _generate_porch(self, element: Dict[str, Any], material: str) -> None:
        """Generate a covered porch/entrance."""
        position = element.get("position")
        dimensions = element.get("dimensions", [5, 3, 3])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        # Floor
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} {material}")
        # Support posts
        self.commands.append(f"/fill {x} {y+1} {z+d-1} {x} {y+h-1} {z+d-1} oak_fence")
        self.commands.append(f"/fill {x+w-1} {y+1} {z+d-1} {x+w-1} {y+h-1} {z+d-1} oak_fence")
        # Roof
        self.commands.append(f"/fill {x} {y+h} {z} {x+w-1} {y+h} {z+d-1} oak_slab")

    def _generate_awning(self, element: Dict[str, Any], material: str) -> None:
        """Generate a shop awning."""
        position = element.get("position")
        dimensions = element.get("dimensions", [4, 1, 2])
        if not position:
            return
        x, y, z = position
        w, _, d = dimensions
        color = material if "wool" in material else "red_wool"
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} {color}")

    def _generate_market_stall(self, element: Dict[str, Any], material: str) -> None:
        """Generate a market stall with counter and awning."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Counter
        self.commands.append(f"/fill {x} {y} {z} {x+2} {y} {z} oak_slab[type=top]")
        # Back wall
        self.commands.append(f"/fill {x} {y} {z+1} {x+2} {y+2} {z+1} oak_planks")
        # Support posts
        self.commands.append(f"/fill {x} {y+1} {z} {x} {y+2} {z} oak_fence")
        self.commands.append(f"/fill {x+2} {y+1} {z} {x+2} {y+2} {z} oak_fence")
        # Awning
        self.commands.append(f"/fill {x} {y+3} {z-1} {x+2} {y+3} {z+1} red_wool")
        # Items on counter
        self.commands.append(f"/setblock {x+1} {y+1} {z} barrel")

    def _generate_stable(self, element: Dict[str, Any], material: str) -> None:
        """Generate an animal stable."""
        position = element.get("position")
        dimensions = element.get("dimensions", [6, 4, 5])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        # Walls (half-height)
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y+1} {z+d-1} {material} hollow")
        # Fence top
        self.commands.append(f"/fill {x} {y+2} {z} {x+w-1} {y+2} {z} oak_fence")
        self.commands.append(f"/fill {x} {y+2} {z+d-1} {x+w-1} {y+2} {z+d-1} oak_fence")
        # Roof
        self.commands.append(f"/fill {x} {y+h-1} {z} {x+w-1} {y+h-1} {z+d-1} oak_slab")
        # Hay
        self.commands.append(f"/setblock {x+1} {y} {z+1} hay_block")

    def _generate_pen(self, element: Dict[str, Any], material: str) -> None:
        """Generate an animal pen with fence."""
        position = element.get("position")
        dimensions = element.get("dimensions", [7, 2, 7])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        fence = material if "fence" in material else "oak_fence"
        # Fence perimeter
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y+h-1} {z} {fence}")
        self.commands.append(f"/fill {x} {y} {z+d-1} {x+w-1} {y+h-1} {z+d-1} {fence}")
        self.commands.append(f"/fill {x} {y} {z} {x} {y+h-1} {z+d-1} {fence}")
        self.commands.append(f"/fill {x+w-1} {y} {z} {x+w-1} {y+h-1} {z+d-1} {fence}")
        # Gate
        self.commands.append(f"/setblock {x+w//2} {y} {z} oak_fence_gate")

    def _generate_dock(self, element: Dict[str, Any], material: str) -> None:
        """Generate a wooden dock/pier."""
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 1, 8])
        if not position:
            return
        x, y, z = position
        w, _, d = dimensions
        plank = material if "planks" in material else "oak_planks"
        # Main deck
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y} {z+d-1} {plank}")
        # Support posts going into water
        self.commands.append(f"/fill {x} {y-2} {z} {x} {y-1} {z} oak_fence")
        self.commands.append(f"/fill {x+w-1} {y-2} {z} {x+w-1} {y-1} {z} oak_fence")
        self.commands.append(f"/fill {x} {y-2} {z+d-1} {x} {y-1} {z+d-1} oak_fence")
        self.commands.append(f"/fill {x+w-1} {y-2} {z+d-1} {x+w-1} {y-1} {z+d-1} oak_fence")

    def _generate_banner(self, element: Dict[str, Any], material: str) -> None:
        """Generate a banner/flag."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        color = material if "_banner" in material else "red_banner"
        self.commands.append(f"/setblock {x} {y} {z} {color}")

    def _generate_sign(self, element: Dict[str, Any]) -> None:
        """Generate a sign."""
        position = element.get("position")
        orientation = element.get("orientation", "south")
        if not position:
            return
        x, y, z = position
        self.commands.append(f"/setblock {x} {y} {z} oak_sign[rotation=8]")

    def _generate_moat(self, element: Dict[str, Any]) -> None:
        """Generate a water moat around a structure."""
        position = element.get("position")
        dimensions = element.get("dimensions", [20, 3, 20])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        # Outer trench
        self.commands.append(f"/fill {x} {y-h+1} {z} {x+w-1} {y} {z+2} water")
        self.commands.append(f"/fill {x} {y-h+1} {z+d-3} {x+w-1} {y} {z+d-1} water")
        self.commands.append(f"/fill {x} {y-h+1} {z} {x+2} {y} {z+d-1} water")
        self.commands.append(f"/fill {x+w-3} {y-h+1} {z} {x+w-1} {y} {z+d-1} water")

    def _generate_gate(self, element: Dict[str, Any], material: str) -> None:
        """Generate a fence gate."""
        position = element.get("position")
        orientation = element.get("orientation", "south")
        if not position:
            return
        x, y, z = position
        gate = material if "gate" in material else "oak_fence_gate"
        self.commands.append(f"/setblock {x} {y} {z} {gate}[facing={orientation}]")

    def _generate_portcullis(self, element: Dict[str, Any]) -> None:
        """Generate an iron bar portcullis gate."""
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 4, 1])
        if not position:
            return
        x, y, z = position
        w, h, _ = dimensions
        self.commands.append(f"/fill {x} {y} {z} {x+w-1} {y+h-1} {z} iron_bars")

    def _generate_battlement(self, element: Dict[str, Any], material: str) -> None:
        """Generate crenellations/battlements on a wall."""
        position = element.get("position")
        dimensions = element.get("dimensions", [10, 2, 1])
        if not position:
            return
        x, y, z = position
        w, h, _ = dimensions
        # Alternating pattern
        for i in range(0, w, 2):
            self.commands.append(f"/fill {x+i} {y} {z} {x+i} {y+h-1} {z} {material}")

    def _generate_arrow_slit(self, element: Dict[str, Any]) -> None:
        """Generate narrow arrow slit windows."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        self.commands.append(f"/setblock {x} {y} {z} air")
        self.commands.append(f"/setblock {x} {y+1} {z} air")

    def _generate_throne(self, element: Dict[str, Any]) -> None:
        """Generate a royal throne."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Seat (stairs)
        self.commands.append(f"/setblock {x} {y} {z} quartz_stairs[facing=south]")
        # Back
        self.commands.append(f"/fill {x} {y+1} {z+1} {x} {y+2} {z+1} quartz_block")
        # Armrests
        self.commands.append(f"/setblock {x-1} {y} {z} quartz_slab[type=top]")
        self.commands.append(f"/setblock {x+1} {y} {z} quartz_slab[type=top]")
        # Gold accents
        self.commands.append(f"/setblock {x} {y+3} {z+1} gold_block")

    def _generate_altar(self, element: Dict[str, Any]) -> None:
        """Generate a ceremonial altar."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Base
        self.commands.append(f"/fill {x-1} {y} {z-1} {x+1} {y} {z+1} stone_bricks")
        # Top
        self.commands.append(f"/setblock {x} {y+1} {z} polished_andesite")
        # Candles
        self.commands.append(f"/setblock {x-1} {y+1} {z} candle[lit=true]")
        self.commands.append(f"/setblock {x+1} {y+1} {z} candle[lit=true]")

    def _generate_statue(self, element: Dict[str, Any], material: str) -> None:
        """Generate a simple statue."""
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 4, 1])
        if not position:
            return
        x, y, z = position
        _, h, _ = dimensions
        block = material if material else "stone"
        # Pedestal
        self.commands.append(f"/fill {x-1} {y} {z-1} {x+1} {y} {z+1} {block}")
        # Figure
        self.commands.append(f"/fill {x} {y+1} {z} {x} {y+h-1} {z} {block}")
        self.commands.append(f"/setblock {x} {y+h} {z} player_head")

    def _generate_obelisk(self, element: Dict[str, Any], material: str) -> None:
        """Generate a tall obelisk."""
        position = element.get("position")
        dimensions = element.get("dimensions", [1, 8, 1])
        if not position:
            return
        x, y, z = position
        _, h, _ = dimensions
        block = material if material else "quartz_block"
        self.commands.append(f"/fill {x} {y} {z} {x} {y+h-1} {z} {block}")
        # Pointed top
        self.commands.append(f"/setblock {x} {y+h} {z} quartz_pillar")

    def _generate_pyramid(self, element: Dict[str, Any], material: str) -> None:
        """Generate a stepped pyramid."""
        position = element.get("position")
        dimensions = element.get("dimensions", [9, 5, 9])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        block = material if material else "sandstone"
        # Build layers
        for layer in range(h):
            offset = layer
            lw = w - (layer * 2)
            ld = d - (layer * 2)
            if lw > 0 and ld > 0:
                self.commands.append(f"/fill {x+offset} {y+layer} {z+offset} {x+offset+lw-1} {y+layer} {z+offset+ld-1} {block}")

    def _generate_dome(self, element: Dict[str, Any], material: str) -> None:
        """Generate a simple dome shape."""
        position = element.get("position")
        dimensions = element.get("dimensions", [7, 4, 7])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        block = material if material else "stone_bricks"
        # Approximate dome with layers
        cx, cz = x + w//2, z + d//2
        for layer in range(h):
            radius = (h - layer)
            self.commands.append(f"/fill {cx-radius} {y+layer} {cz-radius} {cx+radius} {y+layer} {cz+radius} {block} hollow")

    def _generate_spire(self, element: Dict[str, Any], material: str) -> None:
        """Generate a pointed spire/steeple."""
        position = element.get("position")
        dimensions = element.get("dimensions", [3, 8, 3])
        if not position:
            return
        x, y, z = position
        w, h, d = dimensions
        block = material if material else "stone_bricks"
        cx, cz = x + w//2, z + d//2
        # Tapered tower
        for layer in range(h):
            if layer < h - 2:
                self.commands.append(f"/fill {cx-1} {y+layer} {cz-1} {cx+1} {y+layer} {cz+1} {block} hollow")
            elif layer < h - 1:
                self.commands.append(f"/setblock {cx} {y+layer} {cz} {block}")
        # Point
        self.commands.append(f"/setblock {cx} {y+h-1} {cz} lightning_rod")

    def _generate_windmill(self, element: Dict[str, Any]) -> None:
        """Generate a windmill structure."""
        position = element.get("position")
        if not position:
            return
        x, y, z = position
        # Base tower
        self.commands.append(f"/fill {x} {y} {z} {x+4} {y+8} {z+4} cobblestone hollow")
        # Cap
        self.commands.append(f"/fill {x} {y+9} {z} {x+4} {y+9} {z+4} oak_planks")
        # Door
        self.commands.append(f"/setblock {x+2} {y+1} {z} oak_door[facing=south,half=lower]")
        self.commands.append(f"/setblock {x+2} {y+2} {z} oak_door[facing=south,half=upper]")
        # Blades (simplified)
        self.commands.append(f"/fill {x+2} {y+6} {z-1} {x+2} {y+6} {z-4} oak_fence")
        self.commands.append(f"/fill {x+2} {y+6} {z+5} {x+2} {y+6} {z+8} oak_fence")
        self.commands.append(f"/fill {x-1} {y+6} {z+2} {x-4} {y+6} {z+2} oak_fence")
        self.commands.append(f"/fill {x+5} {y+6} {z+2} {x+8} {y+6} {z+2} oak_fence")
    
    def validate_commands(self) -> Tuple[bool, List[str]]:
        """
        Validate all generated commands.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        for i, cmd in enumerate(self.commands):
            # Check basic syntax
            if not cmd.startswith("/"):
                errors.append(f"Command {i}: Missing leading /")
            
            # Check max length (Minecraft chat limit is ~256, but commands can be longer)
            if len(cmd) > 32000:
                errors.append(f"Command {i}: Too long ({len(cmd)} chars)")
            
            # Check for valid block names
            parts = cmd.split()
            if len(parts) > 0 and parts[0] in ["/fill", "/setblock"]:
                # Extract block name
                block = None
                if parts[0] == "/fill":
                    block = parts[7] if len(parts) > 7 else None
                elif parts[0] == "/setblock":
                    block = parts[4] if len(parts) > 4 else None
                
                if block and not self._is_valid_block(block):
                    errors.append(f"Command {i}: Unknown block '{block}'")
        
        return len(errors) == 0, errors
    
    def _is_valid_block(self, block_name: str) -> bool:
        """Check if block name is valid (basic check)"""
        # Remove properties like [facing=north]
        if "[" in block_name:
            block_name = block_name.split("[")[0]
        
        # Common blocks - in production, load from full Minecraft wiki
        valid_blocks = {
            "stone", "dirt", "grass_block", "oak_log", "oak_planks",
            "oak_door", "oak_stairs", "glass", "glass_pane",
            "birch_log", "birch_planks", "spruce_log", "spruce_planks",
            "dark_oak_log", "dark_oak_planks", "dark_oak_stairs",
            "stone_brick", "cobblestone", "torch", "lantern",
            "flower_pot", "carpet", "oak_roof", "dark_oak_stairs"
        }
        
        return block_name in valid_blocks or block_name == "air"


if __name__ == "__main__":
    # Test command generation
    generator = CommandGenerator()
    
    test_blueprint = {
        "structure": {"width": 10, "depth": 10, "height": 4},
        "elements": [
            {"type": "wall", "material": "oak_planks", "position": [0, 0, 0], "dimensions": [10, 4, 10]},
            {"type": "door", "material": "oak_door", "position": [5, 0, 0], "orientation": "south"}
        ],
        "build_order": ["wall", "door"]
    }
    
    commands = generator.generate(test_blueprint)
    print(f"Generated {len(commands)} commands:")
    for cmd in commands:
        print(f"  {cmd}")
    
    valid, errors = generator.validate_commands()
    print(f"Valid: {valid}")
    if errors:
        for error in errors:
            print(f"  ERROR: {error}")
