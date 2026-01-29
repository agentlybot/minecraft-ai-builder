"""
Command Generator - Blueprint to Minecraft Commands

Converts spatial blueprints into executable Minecraft commands.
Optimizes for:
- Command batching
- Performance (using /fill for large areas)
- Syntax validity
"""

from typing import List, Dict, Any, Tuple


class CommandGenerator:
    """Convert spatial blueprints to Minecraft commands"""
    
    def __init__(self):
        """Initialize command generator"""
        self.commands = []
    
    def generate(self, blueprint: Dict[str, Any]) -> List[str]:
        """
        Generate Minecraft commands from a blueprint.
        
        Args:
            blueprint: Spatial blueprint (from SpatialAnalyzer)
            
        Returns:
            List of Minecraft commands ready to execute
        """
        self.commands = []
        
        # Extract structure info
        structure = blueprint.get("structure", {})
        elements = blueprint.get("elements", [])
        
        # Build order
        build_order = blueprint.get("build_order", [])
        
        # Generate commands for each build step
        for step in build_order:
            step_elements = [e for e in elements if e.get("type") == step]
            for element in step_elements:
                self._generate_element_commands(element, structure)
        
        return self.commands
    
    def _generate_element_commands(self, element: Dict[str, Any], structure: Dict[str, Any]) -> None:
        """Generate commands for a single element"""
        
        elem_type = element.get("type")
        material = element.get("material", "stone")
        
        if elem_type == "wall":
            self._generate_fill(element, material)
        elif elem_type == "floor":
            self._generate_fill(element, material)
        elif elem_type == "door":
            self._generate_setblock(element, material)
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
        elif elem_type in ["stairs", "roof"]:
            self._generate_setblock(element, material)
        elif elem_type == "decoration":
            self._generate_setblock(element, material)
    
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
