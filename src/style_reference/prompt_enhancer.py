"""
Prompt Enhancer

Injects style reference data into AI prompts based on
build description and available style references.
"""

import os
import json
from typing import Dict, Any, List, Optional
import re

from .aggregator import AggregatedStyle


# Keywords that map to style categories
# Order matters - first match wins, so put specific categories before general ones
CATEGORY_KEYWORDS = {
    'estate': ['estate', 'manor', 'mansion', 'villa', 'chateau', 'german'],
    'hotel': ['hotel', 'inn', 'tavern', 'hostel', 'lodge', 'guesthouse', 'barrel inn', 'pub'],
    'industrial': ['industrial', 'blacksmith', 'forge', 'workshop', 'factory', 'foundry',
                   'machine', 'smith', 'craftsman'],
    'medieval': ['medieval', 'castle', 'cottage', 'tudor', 'half-timbered',
                 'knight', 'kingdom', 'fortress', 'keep'],
    'modern': ['modern', 'contemporary', 'minimalist', 'glass', 'skyscraper', 'office'],
    'fantasy': ['fantasy', 'wizard', 'magical', 'elven', 'dwarven', 'enchanted', 'tower'],
    'asian': ['asian', 'japanese', 'chinese', 'pagoda', 'temple', 'dojo', 'shrine'],
    'rustic': ['rustic', 'farm', 'barn', 'cabin', 'log', 'homestead', 'ranch'],
    'victorian': ['victorian', 'gothic', 'haunted', 'ornate']
}


class PromptEnhancer:
    """Enhances AI prompts with style reference data."""

    def __init__(self, catalog_path: Optional[str] = None):
        """
        Initialize the prompt enhancer.

        Args:
            catalog_path: Path to the style catalog JSON file.
                         Defaults to examples/style_references/catalog.json
        """
        if catalog_path is None:
            # Default catalog location
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            catalog_path = os.path.join(base_dir, 'examples', 'style_references', 'catalog.json')

        self.catalog_path = catalog_path
        self.catalog: Dict[str, AggregatedStyle] = {}
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Load the style catalog from disk."""
        if not os.path.exists(self.catalog_path):
            return

        try:
            with open(self.catalog_path, 'r') as f:
                data = json.load(f)

            for category, style_data in data.get('categories', {}).items():
                self.catalog[category] = self._dict_to_aggregated_style(style_data)

        except Exception as e:
            print(f"Warning: Could not load style catalog: {e}")

    def _dict_to_aggregated_style(self, data: Dict[str, Any]) -> AggregatedStyle:
        """Convert a dict to AggregatedStyle object."""
        construction = data.get('construction', {})
        return AggregatedStyle(
            category=data.get('category', 'general'),
            example_count=data.get('example_count', 0),
            recommended_walls=data.get('materials', {}).get('walls', []),
            recommended_roof=data.get('materials', {}).get('roof', []),
            recommended_frame=data.get('materials', {}).get('frame', []),
            recommended_foundation=data.get('materials', {}).get('foundation', []),
            recommended_decoration=data.get('materials', {}).get('decoration', []),
            avg_width_height_ratio=data.get('proportions', {}).get('width_height_ratio', 1.5),
            avg_floors=data.get('proportions', {}).get('typical_floors', 2),
            typical_footprint=data.get('proportions', {}).get('typical_footprint', '10x10'),
            common_roof_style=data.get('patterns', {}).get('roof_style', 'peaked'),
            common_wall_style=data.get('patterns', {}).get('wall_style', 'solid'),
            common_foundation_style=data.get('patterns', {}).get('foundation_style', 'stone'),
            common_features=data.get('patterns', {}).get('features', []),
            target_block_variety=data.get('quality_targets', {}).get('block_variety', 15),
            target_window_count=data.get('quality_targets', {}).get('window_count', '4-8'),
            floor_height=construction.get('floor_height', 4),
            window_y_offset=construction.get('window_y_offset', 2),
            window_height=construction.get('window_height', 2),
            window_spacing=construction.get('window_spacing', 3.0),
            door_y_offset=construction.get('door_y_offset', 1),
            frame_post_spacing=construction.get('frame_post_spacing', 4.0),
            frame_post_height=construction.get('frame_post_height', 3),
            foundation_height=construction.get('foundation_height', 1),
            roof_overhang=construction.get('roof_overhang', 1),
            sources=data.get('sources', [])
        )

    def detect_category(self, description: str) -> Optional[str]:
        """
        Detect the style category from a build description.

        Args:
            description: The build description

        Returns:
            Category name or None if no match
        """
        desc_lower = description.lower()

        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in desc_lower for kw in keywords):
                return category

        return None

    def get_style_section(self, category: str) -> Optional[str]:
        """
        Generate a style reference section for a category.

        Args:
            category: The style category

        Returns:
            Formatted style reference text or None if category not found
        """
        if category not in self.catalog:
            return None

        style = self.catalog[category]

        # Build the style section
        lines = [
            f"=== STYLE REFERENCE: {category.upper()} ===",
            f"Based on analysis of {style.example_count} high-quality example builds:",
            "",
            "RECOMMENDED MATERIALS:",
        ]

        if style.recommended_walls:
            lines.append(f"- Primary walls: {', '.join(style.recommended_walls)}")
        if style.recommended_roof:
            lines.append(f"- Roof: {', '.join(style.recommended_roof)}")
        if style.recommended_frame:
            lines.append(f"- Frame: {', '.join(style.recommended_frame)}")
        if style.recommended_foundation:
            lines.append(f"- Foundation: {', '.join(style.recommended_foundation)}")

        lines.extend([
            "",
            "TYPICAL PROPORTIONS:",
            f"- Width-to-height ratio: {style.avg_width_height_ratio}",
            f"- Typical floor count: {style.avg_floors}",
            f"- Typical footprint: {style.typical_footprint}",
            "",
            "ARCHITECTURAL PATTERNS:",
            f"- Roof style: {style.common_roof_style} (ALWAYS use stairs for peaked roofs)",
            f"- Wall style: {style.common_wall_style}",
            f"- Foundation: {style.common_foundation_style}",
        ])

        if style.common_features:
            lines.append(f"- Include: {', '.join(style.common_features)}")

        lines.extend([
            "",
            "CONSTRUCTION RULES (critical for proper building):",
            f"- Floor height: {style.floor_height} blocks between floors",
            f"- Windows: Place at Y+{style.window_y_offset} from floor, {style.window_height} blocks tall, ~{round(style.window_spacing, 1)} blocks apart",
            f"- Doors: Place at Y+{style.door_y_offset} from floor level",
            f"- Frame posts: Every ~{round(style.frame_post_spacing, 1)} blocks, {style.frame_post_height} blocks tall",
            f"- Foundation: {style.foundation_height} block(s) of stone/cobblestone above ground",
            f"- Roof overhang: Extend {style.roof_overhang} block(s) past walls",
            "",
            "DETAIL REQUIREMENTS (CRITICAL - builds must be highly detailed):",
            f"- Use {style.target_block_variety}+ different block types for texture variety",
            "- NEVER use single large fills - break walls into: frame posts + infill sections + trim",
            "- Every window MUST have: glass_pane + trapdoor shutters on sides + slab windowsill",
            "- Every door MUST have: door block + stairs for steps + lantern above",
            "- Walls MUST have: corner posts (logs) + horizontal beams + infill panels between",
            "- Roof MUST have: stairs in layers creating peak + upside-down stairs under eaves",
            "- Add exterior details: barrels, flower pots, lanterns on walls, crates, benches",
            "- Foundation must be visible cobblestone/stone extending past walls",
            "- Generate 100+ elements minimum, 200+ for larger builds",
            "",
            "=== END STYLE REFERENCE ==="
        ])

        return '\n'.join(lines)

    def enhance_prompt(self, base_prompt: str, description: str) -> str:
        """
        Enhance a base prompt with style reference data.

        Args:
            base_prompt: The original system prompt
            description: The build description (used to detect category)

        Returns:
            Enhanced prompt with style reference section
        """
        # Detect category from description
        category = self.detect_category(description)

        if category is None:
            # No matching category, return original prompt
            return base_prompt

        # Get style section
        style_section = self.get_style_section(category)

        if style_section is None:
            # Category detected but no data available
            return base_prompt

        # Insert style section after the first paragraph of the prompt
        # Look for the first double newline
        insert_point = base_prompt.find('\n\n')
        if insert_point == -1:
            # No double newline, append to end
            return base_prompt + '\n\n' + style_section

        # Insert after first paragraph
        return (
            base_prompt[:insert_point + 2] +
            style_section + '\n\n' +
            base_prompt[insert_point + 2:]
        )

    def add_style(self, category: str, style: AggregatedStyle) -> None:
        """
        Add or update a style in the catalog.

        Args:
            category: Category name
            style: AggregatedStyle data
        """
        self.catalog[category] = style

    def save_catalog(self) -> None:
        """Save the catalog to disk."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.catalog_path), exist_ok=True)

        catalog_data = {
            'version': '1.0',
            'categories': {}
        }

        for category, style in self.catalog.items():
            catalog_data['categories'][category] = style.to_dict()

        with open(self.catalog_path, 'w') as f:
            json.dump(catalog_data, f, indent=2)

    def list_categories(self) -> List[str]:
        """List all available style categories."""
        return list(self.catalog.keys())

    def has_category(self, category: str) -> bool:
        """Check if a category exists in the catalog."""
        return category in self.catalog
