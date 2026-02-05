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
