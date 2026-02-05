"""
NBT Parser Module

Parses Minecraft NBT structure files (.nbt) to extract block data
for use as style references in AI-generated builds.
"""

from .parser import NBTParser, parse_nbt_file
from .structure_analyzer import StructureAnalyzer, analyze_structure

__all__ = [
    'NBTParser',
    'parse_nbt_file',
    'StructureAnalyzer',
    'analyze_structure'
]
