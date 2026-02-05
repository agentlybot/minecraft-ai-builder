"""
NBT File Parser

Parses Minecraft NBT structure files using nbtlib to extract
block palette and block positions.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    import nbtlib
    from nbtlib import File, Compound, List as NBTList, Int, Short, ByteArray
except ImportError:
    raise ImportError("nbtlib is required. Install with: pip install nbtlib>=2.0.0")


@dataclass
class Block:
    """Represents a block in the structure."""
    x: int
    y: int
    z: int
    name: str  # e.g., "minecraft:oak_planks"
    properties: Dict[str, str]  # Block state properties


@dataclass
class ParsedStructure:
    """Represents a parsed NBT structure."""
    name: str
    width: int
    height: int
    depth: int
    blocks: List[Block]
    palette: List[str]  # Unique block types used
    author: Optional[str] = None

    @property
    def block_count(self) -> int:
        """Total non-air blocks."""
        return len([b for b in self.blocks if not b.name.endswith(':air')])

    @property
    def dimensions(self) -> Tuple[int, int, int]:
        """Returns (width, height, depth) tuple."""
        return (self.width, self.height, self.depth)


class NBTParser:
    """Parser for Minecraft NBT structure files."""

    def __init__(self):
        self.last_error: Optional[str] = None

    def parse(self, filepath: str) -> Optional[ParsedStructure]:
        """
        Parse an NBT structure file.

        Args:
            filepath: Path to the .nbt file

        Returns:
            ParsedStructure object or None if parsing failed
        """
        if not os.path.exists(filepath):
            self.last_error = f"File not found: {filepath}"
            return None

        try:
            # Load NBT file (structure files are gzipped)
            nbt_file = nbtlib.load(filepath)

            # Get the root compound - structure files have data at root
            root = nbt_file

            # Extract dimensions
            size = root.get('size', [])
            if isinstance(size, NBTList) and len(size) >= 3:
                width = int(size[0])
                height = int(size[1])
                depth = int(size[2])
            else:
                self.last_error = "Could not read structure size"
                return None

            # Extract palette (block types)
            palette_data = root.get('palette', [])
            palette = []
            palette_blocks = []

            for entry in palette_data:
                if isinstance(entry, Compound):
                    block_name = str(entry.get('Name', 'minecraft:air'))
                    properties = {}

                    # Extract block state properties
                    props = entry.get('Properties', {})
                    if isinstance(props, Compound):
                        for key, value in props.items():
                            properties[key] = str(value)

                    palette.append(block_name)
                    palette_blocks.append((block_name, properties))

            # Extract blocks
            blocks_data = root.get('blocks', [])
            blocks = []

            for block_entry in blocks_data:
                if isinstance(block_entry, Compound):
                    # Get position
                    pos = block_entry.get('pos', [])
                    if len(pos) >= 3:
                        x, y, z = int(pos[0]), int(pos[1]), int(pos[2])
                    else:
                        continue

                    # Get block state index
                    state_idx = int(block_entry.get('state', 0))

                    if 0 <= state_idx < len(palette_blocks):
                        block_name, properties = palette_blocks[state_idx]

                        # Skip air blocks
                        if block_name.endswith(':air'):
                            continue

                        blocks.append(Block(
                            x=x,
                            y=y,
                            z=z,
                            name=block_name,
                            properties=properties
                        ))

            # Get structure name from filename
            name = os.path.splitext(os.path.basename(filepath))[0]

            # Try to get author
            author = None
            if 'author' in root:
                author = str(root['author'])

            return ParsedStructure(
                name=name,
                width=width,
                height=height,
                depth=depth,
                blocks=blocks,
                palette=list(set(palette) - {'minecraft:air'}),
                author=author
            )

        except Exception as e:
            self.last_error = f"Parse error: {str(e)}"
            return None


def parse_nbt_file(filepath: str) -> Optional[ParsedStructure]:
    """
    Convenience function to parse an NBT file.

    Args:
        filepath: Path to the .nbt file

    Returns:
        ParsedStructure object or None if parsing failed
    """
    parser = NBTParser()
    result = parser.parse(filepath)
    if result is None:
        print(f"Error parsing NBT: {parser.last_error}")
    return result
