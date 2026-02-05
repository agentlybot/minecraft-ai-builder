"""
Structure Analyzer

Extracts patterns, materials, and quality metrics from parsed NBT structures
to use as style references for AI-generated builds.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import re

from .parser import ParsedStructure, Block


# Block categorization patterns
WALL_BLOCKS = {
    'planks', 'concrete', 'terracotta', 'wool', 'bricks', 'stone_bricks',
    'prismarine', 'quartz', 'sandstone', 'deepslate'
}

ROOF_BLOCKS = {
    'stairs', 'slab', 'shingles'
}

FRAME_BLOCKS = {
    'log', 'stripped', 'wood', 'fence'
}

FLOOR_BLOCKS = {
    'planks', 'stone', 'cobblestone', 'bricks', 'tiles', 'carpet'
}

FOUNDATION_BLOCKS = {
    'cobblestone', 'stone', 'deepslate', 'andesite', 'granite', 'diorite', 'bricks'
}

DECORATION_BLOCKS = {
    'lantern', 'torch', 'flower_pot', 'banner', 'painting', 'item_frame',
    'armor_stand', 'chain', 'bell', 'campfire', 'barrel', 'chest',
    'trapdoor', 'button', 'lever', 'sign', 'candle', 'skull', 'head'
}

GLASS_BLOCKS = {'glass', 'glass_pane', 'tinted_glass'}


@dataclass
class MaterialPalette:
    """Categorized materials from a structure."""
    primary_wall: List[str] = field(default_factory=list)
    roof: List[str] = field(default_factory=list)
    frame: List[str] = field(default_factory=list)
    floor: List[str] = field(default_factory=list)
    foundation: List[str] = field(default_factory=list)
    decoration: List[str] = field(default_factory=list)
    glass: List[str] = field(default_factory=list)
    other: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            'primary_wall': self.primary_wall,
            'roof': self.roof,
            'frame': self.frame,
            'floor': self.floor,
            'foundation': self.foundation,
            'decoration': self.decoration,
            'glass': self.glass,
            'other': self.other
        }


@dataclass
class Proportions:
    """Dimensional proportions of a structure."""
    width: int
    height: int
    depth: int
    width_height_ratio: float
    width_depth_ratio: float
    estimated_floors: int
    footprint_area: int
    volume: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'width': self.width,
            'height': self.height,
            'depth': self.depth,
            'width_height_ratio': round(self.width_height_ratio, 2),
            'width_depth_ratio': round(self.width_depth_ratio, 2),
            'estimated_floors': self.estimated_floors,
            'footprint_area': self.footprint_area,
            'volume': self.volume
        }


@dataclass
class StructuralPatterns:
    """Detected architectural patterns."""
    roof_style: str  # peaked, flat, dome, complex
    wall_style: str  # solid, half_timbered, log, mixed
    foundation_style: str  # stone, brick, none
    features: List[str]  # chimney, porch, balcony, etc.
    symmetry: str  # symmetric, asymmetric

    def to_dict(self) -> Dict[str, Any]:
        return {
            'roof_style': self.roof_style,
            'wall_style': self.wall_style,
            'foundation_style': self.foundation_style,
            'features': self.features,
            'symmetry': self.symmetry
        }


@dataclass
class QualityMetrics:
    """Quality and detail metrics."""
    block_variety: int  # Number of unique block types
    decoration_density: float  # Decorations per volume
    window_count: int
    door_count: int
    detail_score: float  # 0-10 scale

    def to_dict(self) -> Dict[str, Any]:
        return {
            'block_variety': self.block_variety,
            'decoration_density': round(self.decoration_density, 4),
            'window_count': self.window_count,
            'door_count': self.door_count,
            'detail_score': round(self.detail_score, 1)
        }


@dataclass
class StructureMetrics:
    """Complete metrics for a structure."""
    name: str
    materials: MaterialPalette
    proportions: Proportions
    patterns: StructuralPatterns
    quality: QualityMetrics
    top_blocks: List[Tuple[str, int]]  # (block_name, count) sorted by frequency

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'materials': self.materials.to_dict(),
            'proportions': self.proportions.to_dict(),
            'patterns': self.patterns.to_dict(),
            'quality': self.quality.to_dict(),
            'top_blocks': [{'block': b, 'count': c} for b, c in self.top_blocks[:15]]
        }


class StructureAnalyzer:
    """Analyzes parsed structures to extract patterns and metrics."""

    def __init__(self):
        pass

    def analyze(self, structure: ParsedStructure) -> StructureMetrics:
        """
        Analyze a parsed structure and extract all metrics.

        Args:
            structure: A ParsedStructure from NBT parser

        Returns:
            StructureMetrics with all extracted data
        """
        # Count blocks by type
        block_counts = Counter()
        for block in structure.blocks:
            # Simplify name (remove minecraft: prefix)
            simple_name = block.name.replace('minecraft:', '')
            block_counts[simple_name] += 1

        # Categorize materials
        materials = self._categorize_materials(block_counts)

        # Calculate proportions
        proportions = self._calculate_proportions(structure)

        # Detect patterns
        patterns = self._detect_patterns(structure, block_counts, materials)

        # Calculate quality metrics
        quality = self._calculate_quality(structure, block_counts)

        # Get top blocks by frequency
        top_blocks = block_counts.most_common(15)

        return StructureMetrics(
            name=structure.name,
            materials=materials,
            proportions=proportions,
            patterns=patterns,
            quality=quality,
            top_blocks=top_blocks
        )

    def _categorize_materials(self, block_counts: Counter) -> MaterialPalette:
        """Categorize blocks into material types."""
        palette = MaterialPalette()

        for block_name, count in block_counts.items():
            block_lower = block_name.lower()

            # Check each category
            if any(w in block_lower for w in GLASS_BLOCKS):
                palette.glass.append(block_name)
            elif any(w in block_lower for w in DECORATION_BLOCKS):
                palette.decoration.append(block_name)
            elif any(w in block_lower for w in ROOF_BLOCKS):
                palette.roof.append(block_name)
            elif any(w in block_lower for w in FRAME_BLOCKS):
                palette.frame.append(block_name)
            elif any(w in block_lower for w in FOUNDATION_BLOCKS) and count < block_counts.total() * 0.3:
                # Foundation blocks are typically at bottom, less than 30% of total
                palette.foundation.append(block_name)
            elif any(w in block_lower for w in WALL_BLOCKS):
                palette.primary_wall.append(block_name)
            elif any(w in block_lower for w in FLOOR_BLOCKS):
                palette.floor.append(block_name)
            else:
                palette.other.append(block_name)

        return palette

    def _calculate_proportions(self, structure: ParsedStructure) -> Proportions:
        """Calculate dimensional proportions."""
        w, h, d = structure.width, structure.height, structure.depth

        # Estimate floor count (assume ~4 blocks per floor including ceiling)
        estimated_floors = max(1, h // 4)

        return Proportions(
            width=w,
            height=h,
            depth=d,
            width_height_ratio=w / max(h, 1),
            width_depth_ratio=w / max(d, 1),
            estimated_floors=estimated_floors,
            footprint_area=w * d,
            volume=w * h * d
        )

    def _detect_patterns(self, structure: ParsedStructure,
                         block_counts: Counter,
                         materials: MaterialPalette) -> StructuralPatterns:
        """Detect architectural patterns from block placement."""

        # Detect roof style
        roof_style = self._detect_roof_style(structure, block_counts)

        # Detect wall style
        wall_style = self._detect_wall_style(materials, block_counts)

        # Detect foundation
        foundation_style = self._detect_foundation_style(materials)

        # Detect features
        features = self._detect_features(structure, block_counts)

        # Check symmetry (simplified)
        symmetry = self._check_symmetry(structure)

        return StructuralPatterns(
            roof_style=roof_style,
            wall_style=wall_style,
            foundation_style=foundation_style,
            features=features,
            symmetry=symmetry
        )

    def _detect_roof_style(self, structure: ParsedStructure,
                           block_counts: Counter) -> str:
        """Detect the roof style from stair placement."""
        stair_blocks = [b for b in structure.blocks
                       if 'stairs' in b.name.lower()]

        if not stair_blocks:
            # Check for slabs at top
            slab_blocks = [b for b in structure.blocks
                         if 'slab' in b.name.lower()]
            if slab_blocks:
                top_y = max(b.y for b in structure.blocks)
                top_slabs = [b for b in slab_blocks if b.y >= top_y - 2]
                if top_slabs:
                    return 'flat'
            return 'none'

        # Check Y distribution of stairs
        stair_ys = [b.y for b in stair_blocks]
        y_range = max(stair_ys) - min(stair_ys)

        if y_range >= 3:
            return 'peaked'
        elif y_range >= 1:
            return 'sloped'
        else:
            return 'flat'

    def _detect_wall_style(self, materials: MaterialPalette,
                           block_counts: Counter) -> str:
        """Detect wall construction style."""
        has_frame = len(materials.frame) > 0
        has_infill = len(materials.primary_wall) > 0

        # Count logs vs planks
        log_count = sum(c for b, c in block_counts.items() if 'log' in b.lower())
        plank_count = sum(c for b, c in block_counts.items() if 'plank' in b.lower())
        white_count = sum(c for b, c in block_counts.items()
                         if 'white' in b.lower() or 'terracotta' in b.lower())

        if has_frame and (white_count > 0 or has_infill):
            return 'half_timbered'
        elif log_count > plank_count:
            return 'log_cabin'
        elif plank_count > 0:
            return 'planks'
        else:
            return 'solid'

    def _detect_foundation_style(self, materials: MaterialPalette) -> str:
        """Detect foundation type."""
        if not materials.foundation:
            return 'none'

        foundation_str = ' '.join(materials.foundation).lower()

        if 'cobblestone' in foundation_str:
            return 'cobblestone'
        elif 'brick' in foundation_str:
            return 'brick'
        elif 'stone' in foundation_str:
            return 'stone'
        else:
            return 'mixed'

    def _detect_features(self, structure: ParsedStructure,
                         block_counts: Counter) -> List[str]:
        """Detect architectural features."""
        features = []

        # Check for chimney (vertical stack of brick/cobblestone at high Y)
        brick_blocks = [b for b in structure.blocks
                       if 'brick' in b.name.lower() or 'cobblestone' in b.name.lower()]
        if brick_blocks:
            max_y = max(b.y for b in structure.blocks)
            high_bricks = [b for b in brick_blocks if b.y >= max_y - 3]
            if len(high_bricks) >= 4:
                features.append('chimney')

        # Check for porch (platform extending from building)
        stair_blocks = [b for b in structure.blocks if 'stairs' in b.name.lower()]
        low_stairs = [b for b in stair_blocks if b.y <= 2]
        if len(low_stairs) >= 3:
            features.append('porch')

        # Check for balcony (fences/walls at height)
        fence_blocks = [b for b in structure.blocks if 'fence' in b.name.lower()]
        if fence_blocks:
            high_fences = [b for b in fence_blocks if b.y >= structure.height // 2]
            if len(high_fences) >= 4:
                features.append('balcony')

        # Check for window shutters
        trapdoor_count = sum(c for b, c in block_counts.items() if 'trapdoor' in b.lower())
        if trapdoor_count >= 4:
            features.append('window_shutters')

        # Check for lanterns
        if any('lantern' in b.lower() for b in block_counts.keys()):
            features.append('lanterns')

        # Check for flower decorations
        if any('flower' in b.lower() or 'pot' in b.lower() for b in block_counts.keys()):
            features.append('flower_decorations')

        return features

    def _check_symmetry(self, structure: ParsedStructure) -> str:
        """Check if structure appears symmetric."""
        # Simplified symmetry check - compare block counts on each side
        mid_x = structure.width // 2
        left_count = len([b for b in structure.blocks if b.x < mid_x])
        right_count = len([b for b in structure.blocks if b.x >= mid_x])

        ratio = min(left_count, right_count) / max(left_count, right_count, 1)

        if ratio > 0.85:
            return 'symmetric'
        else:
            return 'asymmetric'

    def _calculate_quality(self, structure: ParsedStructure,
                          block_counts: Counter) -> QualityMetrics:
        """Calculate quality and detail metrics."""
        # Block variety
        variety = len(block_counts)

        # Decoration density
        deco_count = sum(c for b, c in block_counts.items()
                        if any(d in b.lower() for d in DECORATION_BLOCKS))
        volume = structure.width * structure.height * structure.depth
        deco_density = deco_count / max(volume, 1)

        # Window count (glass panes/blocks)
        window_count = sum(c for b, c in block_counts.items()
                          if 'glass' in b.lower())

        # Door count
        door_count = sum(c for b, c in block_counts.items()
                        if 'door' in b.lower())

        # Detail score (0-10)
        # Based on variety, decoration density, and features
        detail_score = min(10, (
            (variety / 5) * 2 +  # Up to 4 points for variety
            (deco_density * 1000) * 2 +  # Up to 4 points for decorations
            (window_count / 10) +  # Up to 1 point for windows
            (door_count / 2)  # Up to 1 point for doors
        ))

        return QualityMetrics(
            block_variety=variety,
            decoration_density=deco_density,
            window_count=window_count,
            door_count=door_count,
            detail_score=detail_score
        )


def analyze_structure(structure: ParsedStructure) -> StructureMetrics:
    """
    Convenience function to analyze a structure.

    Args:
        structure: ParsedStructure from NBT parser

    Returns:
        StructureMetrics with all analysis data
    """
    analyzer = StructureAnalyzer()
    return analyzer.analyze(structure)
