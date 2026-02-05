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
class ConstructionRules:
    """Spatial construction rules extracted from block positions."""
    # Floor information
    floor_levels: List[int] = field(default_factory=list)  # Y coordinates of floors
    floor_height: int = 4  # Blocks between floors (including ceiling)

    # Window placement rules
    window_y_offset: int = 2  # Y offset from floor level
    window_height: int = 2  # Typical window height
    window_h_spacing: float = 3.0  # Horizontal spacing between windows
    windows_per_wall: float = 2.0  # Average windows per wall segment

    # Door placement rules
    door_y_offset: int = 1  # Y offset from floor (usually 1 = on floor)
    door_height: int = 2  # Door height
    door_width: int = 1  # Door width

    # Frame/post rules
    frame_post_spacing: float = 4.0  # Horizontal spacing between frame posts
    frame_post_height: int = 3  # Height of frame posts per floor
    has_corner_posts: bool = True  # Posts at corners
    has_mid_wall_posts: bool = False  # Posts in middle of walls

    # Wall construction
    wall_thickness: int = 1  # Wall thickness
    foundation_height: int = 1  # Foundation blocks above ground
    roof_overhang: int = 1  # Roof extends past walls

    def to_dict(self) -> Dict[str, Any]:
        return {
            'floors': {
                'levels': self.floor_levels,
                'height_between': self.floor_height,
                'count': len(self.floor_levels)
            },
            'windows': {
                'y_offset_from_floor': self.window_y_offset,
                'height': self.window_height,
                'horizontal_spacing': round(self.window_h_spacing, 1),
                'per_wall_average': round(self.windows_per_wall, 1)
            },
            'doors': {
                'y_offset_from_floor': self.door_y_offset,
                'height': self.door_height,
                'width': self.door_width
            },
            'frame': {
                'post_spacing': round(self.frame_post_spacing, 1),
                'post_height': self.frame_post_height,
                'corner_posts': self.has_corner_posts,
                'mid_wall_posts': self.has_mid_wall_posts
            },
            'walls': {
                'thickness': self.wall_thickness,
                'foundation_height': self.foundation_height,
                'roof_overhang': self.roof_overhang
            }
        }

    def to_prompt_rules(self) -> str:
        """Generate human-readable construction rules for AI prompts."""
        lines = [
            "CONSTRUCTION RULES (from example analysis):",
            f"- Floor height: {self.floor_height} blocks between floors",
            f"- Windows: Place at Y+{self.window_y_offset} from floor, {self.window_height} blocks tall, ~{round(self.window_h_spacing, 1)} blocks apart",
            f"- Doors: Place at Y+{self.door_y_offset} from floor, {self.door_height} blocks tall",
            f"- Frame posts: Every ~{round(self.frame_post_spacing, 1)} blocks, {self.frame_post_height} blocks tall per floor",
            f"- Foundation: {self.foundation_height} block(s) of stone above ground",
            f"- Roof overhang: {self.roof_overhang} block(s) past walls",
        ]
        if self.has_corner_posts:
            lines.append("- Always place frame posts at corners")
        return '\n'.join(lines)


@dataclass
class StructureMetrics:
    """Complete metrics for a structure."""
    name: str
    materials: MaterialPalette
    proportions: Proportions
    patterns: StructuralPatterns
    quality: QualityMetrics
    construction: ConstructionRules
    top_blocks: List[Tuple[str, int]]  # (block_name, count) sorted by frequency

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'materials': self.materials.to_dict(),
            'proportions': self.proportions.to_dict(),
            'patterns': self.patterns.to_dict(),
            'quality': self.quality.to_dict(),
            'construction': self.construction.to_dict(),
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

        # Analyze construction rules (spatial relationships)
        construction = self._analyze_construction(structure, block_counts)

        # Get top blocks by frequency
        top_blocks = block_counts.most_common(15)

        return StructureMetrics(
            name=structure.name,
            materials=materials,
            proportions=proportions,
            patterns=patterns,
            quality=quality,
            construction=construction,
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

    def _analyze_construction(self, structure: ParsedStructure,
                              block_counts: Counter) -> ConstructionRules:
        """Analyze spatial construction rules from block positions."""
        rules = ConstructionRules()

        # Detect floor levels
        rules.floor_levels = self._detect_floor_levels(structure)
        if len(rules.floor_levels) >= 2:
            # Calculate average floor height
            diffs = [rules.floor_levels[i+1] - rules.floor_levels[i]
                    for i in range(len(rules.floor_levels) - 1)]
            rules.floor_height = round(sum(diffs) / len(diffs))

        # Analyze window placement
        window_rules = self._analyze_window_placement(structure, rules.floor_levels)
        rules.window_y_offset = window_rules.get('y_offset', 2)
        rules.window_height = window_rules.get('height', 2)
        rules.window_h_spacing = window_rules.get('h_spacing', 3.0)
        rules.windows_per_wall = window_rules.get('per_wall', 2.0)

        # Analyze door placement
        door_rules = self._analyze_door_placement(structure, rules.floor_levels)
        rules.door_y_offset = door_rules.get('y_offset', 1)
        rules.door_height = door_rules.get('height', 2)

        # Analyze frame/post spacing
        frame_rules = self._analyze_frame_spacing(structure)
        rules.frame_post_spacing = frame_rules.get('h_spacing', 4.0)
        rules.frame_post_height = frame_rules.get('height', 3)
        rules.has_corner_posts = frame_rules.get('corner_posts', True)
        rules.has_mid_wall_posts = frame_rules.get('mid_posts', False)

        # Analyze wall construction
        wall_rules = self._analyze_wall_construction(structure, rules.floor_levels)
        rules.foundation_height = wall_rules.get('foundation_height', 1)
        rules.roof_overhang = wall_rules.get('roof_overhang', 1)

        return rules

    def _detect_floor_levels(self, structure: ParsedStructure) -> List[int]:
        """Detect Y levels that contain floor surfaces."""
        # Find blocks that are likely floor materials
        floor_blocks = [b for b in structure.blocks
                       if any(f in b.name.lower() for f in ['plank', 'stone', 'brick', 'slab', 'cobble'])]

        if not floor_blocks:
            return [0]

        # Count blocks at each Y level
        y_counts = Counter(b.y for b in floor_blocks)

        # Find Y levels with significant horizontal surfaces
        # (more blocks than would be in a single column)
        min_blocks_for_floor = max(3, structure.width // 2)
        floor_levels = sorted([y for y, count in y_counts.items()
                               if count >= min_blocks_for_floor])

        # Filter out levels that are too close together (within 2 blocks)
        if floor_levels:
            filtered = [floor_levels[0]]
            for y in floor_levels[1:]:
                if y - filtered[-1] >= 3:  # At least 3 blocks apart
                    filtered.append(y)
            return filtered

        return [min(b.y for b in structure.blocks)]

    def _analyze_window_placement(self, structure: ParsedStructure,
                                  floor_levels: List[int]) -> Dict[str, Any]:
        """Analyze window placement patterns."""
        # Find glass blocks (windows)
        glass_blocks = [b for b in structure.blocks
                       if 'glass' in b.name.lower()]

        if not glass_blocks or not floor_levels:
            return {'y_offset': 2, 'height': 2, 'h_spacing': 3.0, 'per_wall': 2.0}

        # Calculate Y offset from nearest floor
        y_offsets = []
        for glass in glass_blocks:
            # Find nearest floor below this glass
            floors_below = [f for f in floor_levels if f < glass.y]
            if floors_below:
                nearest_floor = max(floors_below)
                y_offsets.append(glass.y - nearest_floor)

        avg_y_offset = round(sum(y_offsets) / len(y_offsets)) if y_offsets else 2

        # Calculate window height (vertical extent of glass at same x,z)
        glass_by_xz = {}
        for g in glass_blocks:
            key = (g.x, g.z)
            if key not in glass_by_xz:
                glass_by_xz[key] = []
            glass_by_xz[key].append(g.y)

        window_heights = []
        for ys in glass_by_xz.values():
            if len(ys) >= 1:
                window_heights.append(max(ys) - min(ys) + 1)
        avg_height = round(sum(window_heights) / len(window_heights)) if window_heights else 2

        # Calculate horizontal spacing between windows
        # Group windows by Y level and wall (same Z or same X)
        h_spacings = []

        # Windows on Z-facing walls (same Z, varying X)
        glass_by_z = {}
        for g in glass_blocks:
            if g.z not in glass_by_z:
                glass_by_z[g.z] = []
            glass_by_z[g.z].append(g.x)

        for z, xs in glass_by_z.items():
            if len(xs) >= 2:
                xs_sorted = sorted(set(xs))
                for i in range(len(xs_sorted) - 1):
                    spacing = xs_sorted[i+1] - xs_sorted[i]
                    if spacing >= 2:  # Ignore adjacent glass
                        h_spacings.append(spacing)

        # Windows on X-facing walls (same X, varying Z)
        glass_by_x = {}
        for g in glass_blocks:
            if g.x not in glass_by_x:
                glass_by_x[g.x] = []
            glass_by_x[g.x].append(g.z)

        for x, zs in glass_by_x.items():
            if len(zs) >= 2:
                zs_sorted = sorted(set(zs))
                for i in range(len(zs_sorted) - 1):
                    spacing = zs_sorted[i+1] - zs_sorted[i]
                    if spacing >= 2:
                        h_spacings.append(spacing)

        avg_h_spacing = sum(h_spacings) / len(h_spacings) if h_spacings else 3.0

        # Windows per wall (estimate)
        wall_window_counts = list(len(set(xs)) for xs in glass_by_z.values())
        wall_window_counts.extend(len(set(zs)) for zs in glass_by_x.values())
        per_wall = sum(wall_window_counts) / len(wall_window_counts) if wall_window_counts else 2.0

        return {
            'y_offset': max(1, min(avg_y_offset, 3)),  # Clamp to reasonable range
            'height': max(1, min(avg_height, 4)),
            'h_spacing': max(2.0, min(avg_h_spacing, 8.0)),
            'per_wall': max(1.0, per_wall)
        }

    def _analyze_door_placement(self, structure: ParsedStructure,
                                floor_levels: List[int]) -> Dict[str, Any]:
        """Analyze door placement patterns."""
        door_blocks = [b for b in structure.blocks
                      if 'door' in b.name.lower() and 'trap' not in b.name.lower()]

        if not door_blocks or not floor_levels:
            return {'y_offset': 1, 'height': 2}

        # Calculate Y offset from nearest floor
        y_offsets = []
        for door in door_blocks:
            floors_below = [f for f in floor_levels if f <= door.y]
            if floors_below:
                nearest_floor = max(floors_below)
                y_offsets.append(door.y - nearest_floor)

        avg_y_offset = round(sum(y_offsets) / len(y_offsets)) if y_offsets else 1

        # Door height (count vertical door blocks at same x,z)
        door_by_xz = {}
        for d in door_blocks:
            key = (d.x, d.z)
            if key not in door_by_xz:
                door_by_xz[key] = []
            door_by_xz[key].append(d.y)

        heights = [max(ys) - min(ys) + 1 for ys in door_by_xz.values() if ys]
        avg_height = round(sum(heights) / len(heights)) if heights else 2

        return {
            'y_offset': max(0, min(avg_y_offset, 2)),
            'height': max(2, min(avg_height, 3))
        }

    def _analyze_frame_spacing(self, structure: ParsedStructure) -> Dict[str, Any]:
        """Analyze frame post spacing patterns."""
        # Find log/stripped log blocks (frame posts)
        frame_blocks = [b for b in structure.blocks
                       if 'log' in b.name.lower() or 'stripped' in b.name.lower()]

        if not frame_blocks:
            return {'h_spacing': 4.0, 'height': 3, 'corner_posts': True, 'mid_posts': False}

        # Group by X,Z to find vertical posts
        posts_by_xz = {}
        for f in frame_blocks:
            key = (f.x, f.z)
            if key not in posts_by_xz:
                posts_by_xz[key] = []
            posts_by_xz[key].append(f.y)

        # Find posts (vertical runs of 2+ blocks)
        post_positions = []
        post_heights = []
        for (x, z), ys in posts_by_xz.items():
            if len(ys) >= 2:
                post_positions.append((x, z))
                post_heights.append(max(ys) - min(ys) + 1)

        avg_height = round(sum(post_heights) / len(post_heights)) if post_heights else 3

        # Calculate horizontal spacing between posts
        h_spacings = []

        # Check X spacing (posts at same Z)
        posts_by_z = {}
        for x, z in post_positions:
            if z not in posts_by_z:
                posts_by_z[z] = []
            posts_by_z[z].append(x)

        for z, xs in posts_by_z.items():
            if len(xs) >= 2:
                xs_sorted = sorted(xs)
                for i in range(len(xs_sorted) - 1):
                    h_spacings.append(xs_sorted[i+1] - xs_sorted[i])

        # Check Z spacing (posts at same X)
        posts_by_x = {}
        for x, z in post_positions:
            if x not in posts_by_x:
                posts_by_x[x] = []
            posts_by_x[x].append(z)

        for x, zs in posts_by_x.items():
            if len(zs) >= 2:
                zs_sorted = sorted(zs)
                for i in range(len(zs_sorted) - 1):
                    h_spacings.append(zs_sorted[i+1] - zs_sorted[i])

        avg_spacing = sum(h_spacings) / len(h_spacings) if h_spacings else 4.0

        # Check for corner posts
        if post_positions:
            min_x = min(p[0] for p in post_positions)
            max_x = max(p[0] for p in post_positions)
            min_z = min(p[1] for p in post_positions)
            max_z = max(p[1] for p in post_positions)

            corners = [(min_x, min_z), (min_x, max_z), (max_x, min_z), (max_x, max_z)]
            corner_posts = sum(1 for c in corners if c in post_positions) >= 2

            # Check for mid-wall posts
            mid_posts = any(min_x < p[0] < max_x or min_z < p[1] < max_z
                          for p in post_positions)
        else:
            corner_posts = True
            mid_posts = False

        return {
            'h_spacing': max(2.0, min(avg_spacing, 8.0)),
            'height': max(2, min(avg_height, 6)),
            'corner_posts': corner_posts,
            'mid_posts': mid_posts
        }

    def _analyze_wall_construction(self, structure: ParsedStructure,
                                   floor_levels: List[int]) -> Dict[str, Any]:
        """Analyze wall construction patterns."""
        # Foundation height - find stone/cobble blocks at bottom
        foundation_blocks = [b for b in structure.blocks
                           if any(f in b.name.lower()
                                 for f in ['cobble', 'stone_brick', 'andesite', 'granite'])]

        foundation_height = 1
        if foundation_blocks and floor_levels:
            min_floor = min(floor_levels)
            foundation_ys = [b.y for b in foundation_blocks if b.y <= min_floor]
            if foundation_ys:
                foundation_height = max(foundation_ys) - min(foundation_ys) + 1

        # Roof overhang - compare roof extent to wall extent
        roof_blocks = [b for b in structure.blocks
                      if 'stair' in b.name.lower() or 'slab' in b.name.lower()]
        wall_blocks = [b for b in structure.blocks
                      if any(w in b.name.lower() for w in ['plank', 'concrete', 'terracotta'])]

        roof_overhang = 1
        if roof_blocks and wall_blocks:
            roof_min_x = min(b.x for b in roof_blocks)
            roof_max_x = max(b.x for b in roof_blocks)
            wall_min_x = min(b.x for b in wall_blocks)
            wall_max_x = max(b.x for b in wall_blocks)

            overhang_left = wall_min_x - roof_min_x
            overhang_right = roof_max_x - wall_max_x
            roof_overhang = max(0, min(overhang_left, overhang_right, 3))

        return {
            'foundation_height': max(0, min(foundation_height, 3)),
            'roof_overhang': max(0, min(roof_overhang, 3))
        }


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
