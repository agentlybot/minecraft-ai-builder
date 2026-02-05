"""
Style Aggregator

Combines metrics from multiple style references to create
aggregate statistics for a category.
"""

import os
import json
from typing import Dict, Any, List, Optional
from collections import Counter
from dataclasses import dataclass, field

from .extractor import StyleReference


@dataclass
class AggregatedStyle:
    """Aggregated style metrics from multiple examples."""
    category: str
    example_count: int

    # Most common materials by category
    recommended_walls: List[str] = field(default_factory=list)
    recommended_roof: List[str] = field(default_factory=list)
    recommended_frame: List[str] = field(default_factory=list)
    recommended_foundation: List[str] = field(default_factory=list)
    recommended_decoration: List[str] = field(default_factory=list)

    # Typical proportions
    avg_width_height_ratio: float = 0.0
    avg_floors: int = 1
    typical_footprint: str = ""  # e.g., "10x12"

    # Common patterns
    common_roof_style: str = "peaked"
    common_wall_style: str = "solid"
    common_foundation_style: str = "stone"
    common_features: List[str] = field(default_factory=list)

    # Quality targets
    target_block_variety: int = 15
    target_window_count: str = "4-8"

    # Construction rules (spatial relationships)
    floor_height: int = 4
    window_y_offset: int = 2
    window_height: int = 2
    window_spacing: float = 3.0
    door_y_offset: int = 1
    frame_post_spacing: float = 4.0
    frame_post_height: int = 3
    foundation_height: int = 1
    roof_overhang: int = 1

    # Source examples
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'example_count': self.example_count,
            'materials': {
                'walls': self.recommended_walls,
                'roof': self.recommended_roof,
                'frame': self.recommended_frame,
                'foundation': self.recommended_foundation,
                'decoration': self.recommended_decoration
            },
            'proportions': {
                'width_height_ratio': round(self.avg_width_height_ratio, 2),
                'typical_floors': self.avg_floors,
                'typical_footprint': self.typical_footprint
            },
            'patterns': {
                'roof_style': self.common_roof_style,
                'wall_style': self.common_wall_style,
                'foundation_style': self.common_foundation_style,
                'features': self.common_features
            },
            'construction': {
                'floor_height': self.floor_height,
                'window_y_offset': self.window_y_offset,
                'window_height': self.window_height,
                'window_spacing': round(self.window_spacing, 1),
                'door_y_offset': self.door_y_offset,
                'frame_post_spacing': round(self.frame_post_spacing, 1),
                'frame_post_height': self.frame_post_height,
                'foundation_height': self.foundation_height,
                'roof_overhang': self.roof_overhang
            },
            'quality_targets': {
                'block_variety': self.target_block_variety,
                'window_count': self.target_window_count
            },
            'sources': self.sources
        }

    def save_json(self, output_path: str) -> None:
        """Save aggregated style to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class StyleAggregator:
    """Aggregates multiple style references into category statistics."""

    def __init__(self):
        pass

    def aggregate(self, references: List[StyleReference],
                  category: str = "general") -> AggregatedStyle:
        """
        Aggregate multiple style references into category statistics.

        Args:
            references: List of StyleReference objects
            category: Category name for the aggregation

        Returns:
            AggregatedStyle with combined statistics
        """
        if not references:
            return AggregatedStyle(category=category, example_count=0)

        # Collect all materials
        all_walls = Counter()
        all_roof = Counter()
        all_frame = Counter()
        all_foundation = Counter()
        all_decoration = Counter()

        # Collect proportions
        width_height_ratios = []
        floor_counts = []
        footprints = []

        # Collect patterns
        roof_styles = Counter()
        wall_styles = Counter()
        foundation_styles = Counter()
        all_features = Counter()

        # Collect quality metrics
        block_varieties = []
        window_counts = []

        # Collect construction rules
        floor_heights = []
        window_y_offsets = []
        window_heights = []
        window_spacings = []
        door_y_offsets = []
        frame_spacings = []
        frame_heights = []
        foundation_heights = []
        roof_overhangs = []

        # Process each reference
        for ref in references:
            m = ref.metrics

            # Materials (count occurrences across examples)
            for wall in m.materials.primary_wall:
                all_walls[wall] += 1
            for roof in m.materials.roof:
                all_roof[roof] += 1
            for frame in m.materials.frame:
                all_frame[frame] += 1
            for found in m.materials.foundation:
                all_foundation[found] += 1
            for deco in m.materials.decoration:
                all_decoration[deco] += 1

            # Proportions
            width_height_ratios.append(m.proportions.width_height_ratio)
            floor_counts.append(m.proportions.estimated_floors)
            footprints.append((m.proportions.width, m.proportions.depth))

            # Patterns
            roof_styles[m.patterns.roof_style] += 1
            wall_styles[m.patterns.wall_style] += 1
            foundation_styles[m.patterns.foundation_style] += 1
            for feature in m.patterns.features:
                all_features[feature] += 1

            # Quality
            block_varieties.append(m.quality.block_variety)
            window_counts.append(m.quality.window_count)

            # Construction rules
            if hasattr(m, 'construction'):
                c = m.construction
                floor_heights.append(c.floor_height)
                window_y_offsets.append(c.window_y_offset)
                window_heights.append(c.window_height)
                window_spacings.append(c.window_h_spacing)
                door_y_offsets.append(c.door_y_offset)
                frame_spacings.append(c.frame_post_spacing)
                frame_heights.append(c.frame_post_height)
                foundation_heights.append(c.foundation_height)
                roof_overhangs.append(c.roof_overhang)

        # Calculate averages and most common
        n = len(references)

        # Average proportions
        avg_wh_ratio = sum(width_height_ratios) / n
        avg_floors = round(sum(floor_counts) / n)

        # Typical footprint (average dimensions rounded)
        avg_width = round(sum(f[0] for f in footprints) / n)
        avg_depth = round(sum(f[1] for f in footprints) / n)
        typical_footprint = f"{avg_width}x{avg_depth}"

        # Quality targets
        target_variety = round(sum(block_varieties) / n)
        avg_windows = sum(window_counts) / n
        min_windows = max(1, round(avg_windows * 0.5))
        max_windows = round(avg_windows * 1.5)

        # Average construction rules (with defaults)
        avg_floor_height = round(sum(floor_heights) / len(floor_heights)) if floor_heights else 4
        avg_window_y = round(sum(window_y_offsets) / len(window_y_offsets)) if window_y_offsets else 2
        avg_window_h = round(sum(window_heights) / len(window_heights)) if window_heights else 2
        avg_window_space = sum(window_spacings) / len(window_spacings) if window_spacings else 3.0
        avg_door_y = round(sum(door_y_offsets) / len(door_y_offsets)) if door_y_offsets else 1
        avg_frame_space = sum(frame_spacings) / len(frame_spacings) if frame_spacings else 4.0
        avg_frame_h = round(sum(frame_heights) / len(frame_heights)) if frame_heights else 3
        avg_found_h = round(sum(foundation_heights) / len(foundation_heights)) if foundation_heights else 1
        avg_roof_over = round(sum(roof_overhangs) / len(roof_overhangs)) if roof_overhangs else 1

        return AggregatedStyle(
            category=category,
            example_count=n,
            recommended_walls=self._top_items(all_walls, 5),
            recommended_roof=self._top_items(all_roof, 3),
            recommended_frame=self._top_items(all_frame, 3),
            recommended_foundation=self._top_items(all_foundation, 3),
            recommended_decoration=self._top_items(all_decoration, 5),
            avg_width_height_ratio=avg_wh_ratio,
            avg_floors=avg_floors,
            typical_footprint=typical_footprint,
            common_roof_style=roof_styles.most_common(1)[0][0] if roof_styles else "peaked",
            common_wall_style=wall_styles.most_common(1)[0][0] if wall_styles else "solid",
            common_foundation_style=foundation_styles.most_common(1)[0][0] if foundation_styles else "stone",
            common_features=self._top_items(all_features, 5),
            target_block_variety=target_variety,
            target_window_count=f"{min_windows}-{max_windows}",
            floor_height=avg_floor_height,
            window_y_offset=avg_window_y,
            window_height=avg_window_h,
            window_spacing=avg_window_space,
            door_y_offset=avg_door_y,
            frame_post_spacing=avg_frame_space,
            frame_post_height=avg_frame_h,
            foundation_height=avg_found_h,
            roof_overhang=avg_roof_over,
            sources=[ref.name for ref in references]
        )

    def _top_items(self, counter: Counter, n: int) -> List[str]:
        """Get top n items from a counter."""
        return [item for item, _ in counter.most_common(n)]


def aggregate_styles(references: List[StyleReference],
                    category: str = "general",
                    output_json: Optional[str] = None) -> AggregatedStyle:
    """
    Convenience function to aggregate style references.

    Args:
        references: List of StyleReference objects
        category: Category name
        output_json: Optional path to save JSON output

    Returns:
        AggregatedStyle with combined statistics
    """
    aggregator = StyleAggregator()
    result = aggregator.aggregate(references, category)

    if output_json:
        result.save_json(output_json)
        print(f"Saved aggregated style to: {output_json}")

    return result
