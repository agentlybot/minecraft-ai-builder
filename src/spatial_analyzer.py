"""
Spatial Analyzer - AI Integration

Uses OpenAI or Claude to parse natural language descriptions into spatial blueprints.
Handles:
- Material references
- Dimension parsing
- Spatial reasoning
- Structure generation

Now uses templates for known building types (cottage, tavern, etc.) for guaranteed quality,
with AI fallback for custom/unknown builds.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

from building_templates import TEMPLATES, get_template, cottage_template, medieval_house_template, tavern_template
from voxel_blueprints import get_voxel_blueprint, voxel_to_blueprint_format, VOXEL_BLUEPRINTS


class SpatialAnalyzer:
    """Parse natural language into Minecraft spatial blueprints using AI"""

    def __init__(self, provider: str = "openai", model: str = None):
        """
        Initialize with AI client.

        Args:
            provider: "openai" or "anthropic"
            model: Model to use (defaults based on provider)
        """
        self.provider = provider

        if provider == "openai":
            from openai import OpenAI
            self.client = OpenAI()
            # Use gpt-4-turbo for better structured output
            self.model = model or "gpt-4-turbo"
        else:
            import anthropic
            self.client = anthropic.Anthropic()
            self.model = model or "claude-sonnet-4-20250514"

    def _get_system_prompt(self, base_pos: List[int]) -> str:
        bx, by, bz = base_pos[0], base_pos[1], base_pos[2]
        return f"""You are an expert Minecraft architect. You MUST generate HIGHLY DETAILED builds with 50-200+ elements.

CRITICAL RULES:
1. Generate MANY elements (50-200+). Simple builds need 50+, complex builds need 100-200+
2. NEVER use single large fills for walls. Break walls into: frame posts, infill sections, trim
3. ALWAYS include: foundation, frame posts, wall infill, windows with frames, proper peaked roof, decorations
4. Roofs MUST use stairs in a peaked pattern - NEVER flat roofs

Starting position: [{bx}, {by}, {bz}]. Ground Y = {by}.

=== EXAMPLE: SMALL COTTAGE (shows required detail level) ===
For a 7x5 cottage at position [10, -60, 10], you would generate elements like:
{{
  "structure": {{"width": 9, "depth": 7, "height": 8, "ground_level": {by}}},
  "elements": [
    // FOUNDATION (stone base, extends 1 block out)
    {{"type": "floor", "material": "cobblestone", "position": [9, {by}, 9], "dimensions": [11, 1, 9]}},

    // FLOOR (wood, inside foundation)
    {{"type": "floor", "material": "oak_planks", "position": [10, {by}, 10], "dimensions": [7, 1, 5]}},

    // FRAME POSTS (logs at corners - 4 corners)
    {{"type": "column", "material": "stripped_oak_log", "position": [10, {by+1}, 10], "dimensions": [1, 4, 1]}},
    {{"type": "column", "material": "stripped_oak_log", "position": [16, {by+1}, 10], "dimensions": [1, 4, 1]}},
    {{"type": "column", "material": "stripped_oak_log", "position": [10, {by+1}, 14], "dimensions": [1, 4, 1]}},
    {{"type": "column", "material": "stripped_oak_log", "position": [16, {by+1}, 14], "dimensions": [1, 4, 1]}},

    // HORIZONTAL BEAMS (connect posts)
    {{"type": "beam", "material": "stripped_oak_log", "position": [10, {by+4}, 10], "dimensions": [7, 1, 1]}},
    {{"type": "beam", "material": "stripped_oak_log", "position": [10, {by+4}, 14], "dimensions": [7, 1, 1]}},

    // WALL INFILL (between posts - NOT full walls, leave window gaps)
    {{"type": "wall", "material": "white_concrete", "position": [11, {by+1}, 10], "dimensions": [2, 3, 1]}},
    {{"type": "wall", "material": "white_concrete", "position": [14, {by+1}, 10], "dimensions": [2, 3, 1]}},
    // (more wall sections for each side, leaving gaps for windows)

    // WINDOWS (glass panes with trapdoor shutters)
    {{"type": "window", "material": "glass_pane", "position": [13, {by+2}, 10], "dimensions": [1, 2, 1]}},
    {{"type": "decoration", "material": "spruce_trapdoor", "position": [12, {by+2}, 10], "dimensions": [1, 2, 1]}},
    {{"type": "decoration", "material": "spruce_trapdoor", "position": [14, {by+2}, 10], "dimensions": [1, 2, 1]}},

    // ROOF (stairs creating peak - NEVER flat)
    {{"type": "roof", "material": "spruce_stairs", "position": [9, {by+5}, 9], "dimensions": [9, 1, 1], "orientation": "south"}},
    {{"type": "roof", "material": "spruce_stairs", "position": [9, {by+5}, 15], "dimensions": [9, 1, 1], "orientation": "north"}},
    {{"type": "roof", "material": "spruce_stairs", "position": [10, {by+6}, 10], "dimensions": [7, 1, 1], "orientation": "south"}},
    {{"type": "roof", "material": "spruce_stairs", "position": [10, {by+6}, 14], "dimensions": [7, 1, 1], "orientation": "north"}},
    {{"type": "roof", "material": "spruce_slab", "position": [11, {by+7}, 11], "dimensions": [5, 1, 3]}},

    // CHIMNEY
    {{"type": "chimney", "material": "cobblestone", "position": [15, {by+5}, 13], "dimensions": [1, 4, 1]}},

    // DOOR with porch
    {{"type": "porch", "material": "oak_planks", "position": [12, {by}, 8], "dimensions": [3, 1, 2]}},
    {{"type": "door", "material": "oak_door", "position": [13, {by+1}, 10], "orientation": "south"}},

    // DECORATIONS
    {{"type": "lantern", "material": "lantern", "position": [11, {by+3}, 9]}},
    {{"type": "decoration", "material": "barrel", "position": [17, {by+1}, 11]}},
    {{"type": "flower", "material": "rose_bush", "position": [11, {by+1}, 8]}}
    // ... 30+ more decoration elements
  ],
  "build_order": ["floor", "column", "beam", "wall", "window", "door", "roof", "chimney", "porch", "decoration", "lantern", "flower"]
}}

=== THIS IS THE MINIMUM DETAIL LEVEL. Generate MORE elements, not fewer! ===

JSON Schema:
{{
  "structure": {{
    "width": number (include outdoor areas like gardens),
    "depth": number (include outdoor areas),
    "height": number,
    "base_material": string,
    "roof_material": string,
    "description": string,
    "ground_level": {base_pos[1]}
  }},
  "elements": [
    {{
      "type": "floor|wall|door|window|roof|chimney|stairs|decoration|fence|garden|path|flower|lantern|water|pond|fountain|well|crops|farm|tree|torch|lamp|bed|chest|barrel|crafting_table|furnace|anvil|bookshelf|carpet|ladder|trapdoor|table|chair|fireplace|column|pillar|arch|balcony|porch|awning|market_stall|stable|pen|dock|platform|banner|sign|bell|hay|moat|gate|portcullis|battlement|arrow_slit|throne|altar|statue|obelisk|pyramid|dome|spire|windmill|tower|bridge",
      "material": "minecraft_block_name",
      "position": [x, y, z],
      "dimensions": [width, height, depth],
      "orientation": "north|south|east|west" (for doors/stairs),
      "accessible_from": "interior|exterior" (for doors)
    }}
  ],
  "build_order": ["floor", "moat", "wall", "column", "pillar", "arch", "door", "gate", "window", "arrow_slit", "roof", "dome", "spire", "chimney", "stairs", "ladder", "balcony", "porch", "bridge", "battlement", "portcullis", "decoration", "fence", "pen", "stable", "garden", "farm", "crops", "path", "pond", "fountain", "well", "water", "tree", "flower", "lantern", "torch", "lamp", "table", "chair", "bed", "chest", "barrel", "crafting_table", "furnace", "anvil", "bookshelf", "carpet", "fireplace", "throne", "altar", "banner", "sign", "bell", "hay", "awning", "market_stall", "dock", "statue", "obelisk", "pyramid", "windmill"]
}}

=== PROFESSIONAL BUILDING TECHNIQUES ===

CRITICAL: Generate DETAILED builds with DEPTH and LAYERING. Never make flat walls!

=== 1. DEPTH & LAYERING (MOST IMPORTANT) ===
- NOTHING should be flat! Every surface needs depth
- Walls: Recess windows 1 block inward, or add frames that protrude
- Foundation: Extend 1 block outward from walls (stone_bricks or cobblestone)
- Roof overhang: Extend 1-2 blocks beyond walls
- Use upside-down stairs under overhangs for detail
- Add support beams (fence posts, logs) under overhangs

=== 2. HALF-TIMBERED/TUDOR STYLE (for medieval/cottage) ===
Frame construction creates the iconic look:
- FRAME: Use stripped_oak_log or dark_oak_log as vertical posts at corners
- FRAME: Add horizontal stripped logs between floors
- FRAME: Diagonal cross-braces (X pattern) on larger wall sections
- INFILL: Fill between frames with white_concrete, white_terracotta, or birch_planks
- This creates the classic medieval European look

Example wall section (side view):
  [log]  [white]  [white]  [log]
  [log]  [white]  [white]  [log]  <- horizontal beam
  [log]  [white]  [white]  [log]
  [stone] [stone] [stone] [stone] <- foundation

=== 3. ROOF CONSTRUCTION ===
STEEP PITCHED ROOFS with proper detail:
- Use stairs for main roof surface (oak_stairs, spruce_stairs, brick_stairs)
- OVERHANG: Extend roof 1-2 blocks past walls
- Under overhang: Place upside-down stairs for eave detail
- Gable ends: Use stairs + slabs to create triangular end
- DORMERS: Add small roof projections with windows to break up large roofs
- Mix stair types for texture (oak + spruce, or brick + stone)

Roof layers (for 9-wide building):
- Y+0: stairs at x=0 and x=8 (facing inward)
- Y+1: stairs at x=1 and x=7 (facing inward)
- Y+2: stairs at x=2 and x=6 (facing inward)
- Y+3: stairs at x=3 and x=5 (facing inward)
- Y+4: slabs at x=4 (peak)

=== 4. WINDOW DETAILS ===
Windows need frames and depth:
- Use glass_pane (NOT glass blocks) - adds natural depth
- FRAME: Surround with trapdoors, logs, or different plank type
- SHUTTERS: Add trapdoors on sides of windows (spruce_trapdoor)
- WINDOW BOX: Place slab below window, add flower_pot with flowers
- Vary window sizes: 1x1, 1x2, 2x2 for visual interest
- Tall windows: Stack 2-3 glass_panes vertically

=== 5. FOUNDATION & BASE ===
Every building needs a solid foundation:
- MATERIAL: cobblestone, stone_bricks, or andesite
- HEIGHT: 1-2 blocks above ground
- WIDTH: Extend 1 block outward from walls
- Add mossy_cobblestone or cracked_stone_bricks randomly for age

=== 6. MULTI-STORY BUILDINGS ===
For 2+ story buildings:
- Each floor is 4 blocks high (3 interior + 1 floor)
- Add horizontal log beam between floors (visible on exterior)
- Upper floors can overhang lower floors by 1 block (jettying)
- Balconies on upper floors with fence railings

=== 7. CHIMNEY CONSTRUCTION ===
Chimneys add character:
- MATERIAL: cobblestone, stone_bricks, or bricks
- Taper: Start 2x2 at base, narrow to 1x1 at top
- HEIGHT: Extend 2-3 blocks above roof peak
- TOP: Add campfire inside for smoke, or iron_bars cap
- Position: Corner or side of building, not center

=== 8. EXTERIOR DETAILS ===
Scatter these around the building:
- Barrels and crates (barrel block)
- Flower pots on windowsills and by doors
- Lanterns on walls and fence posts
- Hay bales near stables/farms
- Logs/wood piles (oak_log horizontal)
- Carts/wagons (use fences, slabs, trapdoors)
- Signs and banners
- Armor stands, item frames

=== 9. PORCH & ENTRANCE ===
Every door needs an entrance area:
- PORCH: 3x2 platform with fence railing
- ROOF: Extend main roof or add small awning
- SUPPORT: Fence posts or log pillars
- STEPS: Stairs leading up to door
- LIGHTING: Lanterns on posts

=== 10. TEXTURE MIXING ===
Never use just one block type:
- WALLS: Mix oak_planks with spruce_planks accents
- STONE: Mix cobblestone, stone_bricks, andesite
- Add cracked/mossy variants (10-20%) for weathering
- Use stripped logs for beams, regular logs for structure

=== BUILD ORDER (CRITICAL) ===
1. Foundation (stone, extends outward)
2. Floor (planks, at ground level)
3. Frame posts (logs at corners)
4. Walls with window openings (infill between frames)
5. Horizontal beams between floors
6. Second floor (if applicable)
7. Roof structure (stairs with overhang)
8. Roof details (dormers, upside-down stairs under eaves)
9. Chimney
10. Windows (glass_pane with frames)
11. Shutters (trapdoors)
12. Door with porch
13. Interior (floor, furniture)
14. Exterior details (barrels, lanterns, flowers)
15. Pathways and landscaping

=== MATERIALS PALETTE ===
WOOD:
- Planks: oak_planks, spruce_planks, birch_planks, dark_oak_planks
- Logs: oak_log, spruce_log, stripped_oak_log, stripped_spruce_log
- Slabs: oak_slab, spruce_slab, dark_oak_slab
- Stairs: oak_stairs, spruce_stairs, dark_oak_stairs
- Trapdoors: oak_trapdoor, spruce_trapdoor, dark_oak_trapdoor
- Fences: oak_fence, spruce_fence, dark_oak_fence

STONE:
- cobblestone, mossy_cobblestone, stone_bricks, mossy_stone_bricks
- cracked_stone_bricks, andesite, polished_andesite, granite

ROOFING:
- oak_stairs, spruce_stairs, dark_oak_stairs (wood shingles)
- brick_stairs, stone_brick_stairs (tile/slate look)
- cobblestone_stairs (rustic)

INFILL (for half-timbered):
- white_concrete, white_terracotta, birch_planks, smooth_quartz

GLASS: glass_pane (always, never glass blocks)

DECORATION:
- lantern, torch, campfire, flower_pot
- barrel, chest, crafting_table, furnace, anvil
- oak_pressure_plate (for tables), item_frame, armor_stand

FLOWERS: poppy, dandelion, azure_bluet, cornflower, oxeye_daisy, rose_bush, peony
- Decor: flower_pot, crafting_table, furnace, chest, barrel"""

    def _parse_options(self, description: str) -> Dict[str, Any]:
        """Extract options from description like wood type, size, features."""
        desc_lower = description.lower()
        options = {}

        # Wood type detection
        wood_types = ["oak", "spruce", "birch", "dark_oak", "acacia", "jungle", "mangrove", "cherry"]
        for wood in wood_types:
            if wood.replace("_", " ") in desc_lower or wood in desc_lower:
                options["wood_type"] = wood
                break

        # Roof type detection
        if "slate" in desc_lower or "stone" in desc_lower:
            options["roof_type"] = "stone_brick"
        elif "dark" in desc_lower:
            options["roof_type"] = "dark_oak"
        elif "birch" in desc_lower:
            options["roof_type"] = "birch"
        else:
            options["roof_type"] = "spruce"  # Default

        # Feature detection
        options["has_garden"] = any(word in desc_lower for word in ["garden", "flower", "plants"])
        options["has_chimney"] = "no chimney" not in desc_lower

        # Size detection
        if any(word in desc_lower for word in ["small", "tiny", "little"]):
            options["width"] = 7
            options["depth"] = 5
        elif any(word in desc_lower for word in ["large", "big", "grand"]):
            options["width"] = 13
            options["depth"] = 11
        # Otherwise use template defaults

        return options

    def analyze(self, description: str, player_pos: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Parse natural language description into a spatial blueprint.

        Priority order:
        1. Voxel blueprints (most reliable - exact block placement)
        2. Parametric templates (flexible but guaranteed structure)
        3. AI generation (for custom builds)

        Args:
            description: User's natural language description
            player_pos: Optional player position [x, y, z]

        Returns:
            Blueprint dict with structure, elements, build order, etc.
        """
        base_pos = player_pos or [0, 64, 0]
        x, y, z = base_pos

        # Priority 1: Try voxel blueprint (most reliable)
        voxel = get_voxel_blueprint(description)
        if voxel:
            print(f"🧱 Using voxel blueprint: {voxel['name']}")
            blueprint = voxel_to_blueprint_format(voxel, x, y, z)
            block_count = len([e for e in blueprint['elements'] if e['material'] != 'air'])
            print(f"✅ Voxel blueprint: {block_count} blocks to place")
            return blueprint

        # Priority 2: Try parametric template
        template_key = get_template(description)
        if template_key:
            print(f"📋 Using parametric template: {template_key}")
            template_func = TEMPLATES[template_key]
            options = self._parse_options(description)

            # Build with template
            blueprint = template_func(x, y, z, **options)
            print(f"✅ Template generated {len(blueprint['elements'])} elements")
            return blueprint

        # Priority 3: Fall back to AI
        print(f"🤖 No blueprint match, using AI ({self.model})...")
        return self._analyze_with_ai(description, base_pos)

    def _analyze_with_ai(self, description: str, base_pos: List[int]) -> Dict[str, Any]:
        """Use AI to generate blueprint for custom builds."""
        system_prompt = self._get_system_prompt(base_pos)

        user_prompt = f"""Parse this Minecraft build description into a spatial blueprint:

Description: {description}
Build starting position: {base_pos}

Generate elements with EXACT coordinates starting from {base_pos}.
Respond with ONLY valid JSON (no markdown, no explanation)."""

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4096
            )
            response_text = response.choices[0].message.content.strip()
        else:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            response_text = response.content[0].text.strip()

        # Handle markdown code blocks if AI wraps response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        try:
            blueprint = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Log the raw response for debugging
            print(f"❌ JSON Parse Error: {e}")
            print(f"   Response length: {len(response_text)} chars")
            print(f"   First 500 chars: {response_text[:500]}")
            print(f"   Last 200 chars: {response_text[-200:]}")
            raise ValueError(f"AI returned invalid JSON: {str(e)}")

        return blueprint
    
    def refine_blueprint(self, blueprint: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refine a blueprint based on user feedback.
        
        Args:
            blueprint: Original blueprint
            feedback: User feedback (e.g., "make it taller", "add more windows")
            
        Returns:
            Refined blueprint
        """
        # TODO: Implement refinement loop
        pass


if __name__ == "__main__":
    analyzer = SpatialAnalyzer()
    
    # Test analysis
    blueprint = analyzer.analyze(
        "Build a 10x10 oak cabin with a door in front and windows on the sides"
    )
    print(json.dumps(blueprint, indent=2))
