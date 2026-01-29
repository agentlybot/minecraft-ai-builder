"""
Spatial Analyzer - Claude Integration

Uses Claude to parse natural language descriptions into spatial blueprints.
Handles:
- Material references
- Dimension parsing
- Spatial reasoning
- Structure generation
"""

import anthropic
import json
from typing import Dict, Any, List, Optional


class SpatialAnalyzer:
    """Parse natural language into Minecraft spatial blueprints using Claude"""
    
    def __init__(self, model: str = "claude-opus-4-5"):
        """
        Initialize with Claude client.
        
        Args:
            model: Claude model to use for analysis
        """
        self.client = anthropic.Anthropic()
        self.model = model
        
    def analyze(self, description: str, player_pos: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Parse natural language description into a spatial blueprint.
        
        Args:
            description: User's natural language description
            player_pos: Optional player position [x, y, z]
            
        Returns:
            Blueprint dict with structure, elements, build order, etc.
        """
        
        system_prompt = """You are an expert Minecraft architect and spatial reasoner.
Your job is to parse natural language descriptions of Minecraft builds and convert them 
into detailed spatial blueprints.

You MUST respond with valid JSON (no markdown, no extra text) matching this schema:
{
  "structure": {
    "width": number,
    "depth": number,
    "height": number,
    "base_material": string,
    "roof_material": string,
    "description": string
  },
  "elements": [
    {
      "type": "string (wall|door|window|stairs|roof|floor|decoration)",
      "material": "string (minecraft block name)",
      "position": [x, y, z] or null,
      "dimensions": [width, height, depth] or null,
      "quantity": number,
      "orientation": "string (north|south|east|west)" or null
    }
  ],
  "build_order": ["step1", "step2", ...],
  "notes": "any special considerations"
}

Material reference guide:
- Wood: oak_planks, birch_planks, spruce_planks, dark_oak_planks
- Logs: oak_log, birch_log, spruce_log, dark_oak_log
- Doors: oak_door, birch_door, spruce_door, iron_door
- Stairs: oak_stairs, birch_stairs, stone_stairs, etc
- Roof: dark_oak_stairs, oak_stairs, spruce_stairs, etc
- Glass: glass, glass_pane
- Stone: stone, cobblestone, stone_brick
- Decorations: flower_pot, lantern, torch, carpet, etc

Always assume relative positioning from the player's current location.
Consider realistic proportions and building codes."""
        
        user_prompt = f"""Parse this Minecraft build description into a spatial blueprint:

Description: {description}
Player Position: {player_pos or '[0, 64, 0] (estimated)'}

Respond with ONLY valid JSON matching the schema (no markdown, no explanation)."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Parse Claude's response
        response_text = response.content[0].text.strip()
        
        # Handle markdown code blocks if Claude wraps response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        blueprint = json.loads(response_text)
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
