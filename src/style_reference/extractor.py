"""
Style Extractor

High-level API for extracting style metrics from NBT files.
Combines NBT parsing with structure analysis.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nbt_parser import parse_nbt_file, analyze_structure
from nbt_parser.structure_analyzer import StructureMetrics


@dataclass
class StyleReference:
    """A style reference extracted from an NBT file."""
    name: str
    category: str
    source_file: str
    metrics: StructureMetrics

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'category': self.category,
            'source_file': self.source_file,
            'metrics': self.metrics.to_dict()
        }

    def save_json(self, output_path: str) -> None:
        """Save style reference to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class StyleExtractor:
    """Extracts style references from NBT structure files."""

    def __init__(self):
        self.last_error: Optional[str] = None

    def extract(self, nbt_path: str, category: str = "general") -> Optional[StyleReference]:
        """
        Extract a style reference from an NBT file.

        Args:
            nbt_path: Path to the .nbt file
            category: Style category (e.g., "medieval", "modern", "fantasy")

        Returns:
            StyleReference object or None if extraction failed
        """
        # Parse the NBT file
        structure = parse_nbt_file(nbt_path)
        if structure is None:
            self.last_error = "Failed to parse NBT file"
            return None

        # Analyze the structure
        metrics = analyze_structure(structure)

        # Create style reference
        name = os.path.splitext(os.path.basename(nbt_path))[0]

        return StyleReference(
            name=name,
            category=category,
            source_file=nbt_path,
            metrics=metrics
        )

    def extract_directory(self, dir_path: str, category: str = "general") -> List[StyleReference]:
        """
        Extract style references from all NBT files in a directory.

        Args:
            dir_path: Path to directory containing .nbt files
            category: Style category for all files

        Returns:
            List of StyleReference objects
        """
        references = []

        if not os.path.isdir(dir_path):
            self.last_error = f"Not a directory: {dir_path}"
            return references

        for filename in os.listdir(dir_path):
            if filename.endswith('.nbt'):
                filepath = os.path.join(dir_path, filename)
                ref = self.extract(filepath, category)
                if ref:
                    references.append(ref)
                    print(f"  Extracted: {ref.name} ({ref.metrics.quality.block_variety} block types)")
                else:
                    print(f"  Failed: {filename} - {self.last_error}")

        return references


def extract_style_from_nbt(nbt_path: str, category: str = "general",
                          output_json: Optional[str] = None) -> Optional[StyleReference]:
    """
    Convenience function to extract a style reference from an NBT file.

    Args:
        nbt_path: Path to the .nbt file
        category: Style category
        output_json: Optional path to save JSON output

    Returns:
        StyleReference object or None if extraction failed
    """
    extractor = StyleExtractor()
    ref = extractor.extract(nbt_path, category)

    if ref and output_json:
        ref.save_json(output_json)
        print(f"Saved metrics to: {output_json}")

    return ref
