"""
Minecraft AI Builder - Main Orchestrator

Coordinates the entire build pipeline:
1. Parse natural language input (via Claude)
2. Generate Minecraft commands
3. Execute on Minecraft server
4. Report results
"""

from spatial_analyzer import SpatialAnalyzer
from command_generator import CommandGenerator
from server_interface import ServerInterface
import json
from typing import Dict, Any, List


class MinecraftBuilder:
    """Main orchestrator for NLP → Minecraft builds"""
    
    def __init__(self, server_host: str, server_port: int, rcon_password: str):
        """
        Initialize builder with server connection details.
        
        Args:
            server_host: IP/hostname of Minecraft server
            server_port: mcrcon port (default 25575)
            rcon_password: Server rcon password
        """
        self.analyzer = SpatialAnalyzer()
        self.generator = CommandGenerator()
        self.server = ServerInterface(server_host, server_port, rcon_password)
        
    def build(self, description: str, player_pos: List[int] = None) -> Dict[str, Any]:
        """
        Parse description and execute build on server.
        
        Args:
            description: Natural language description (e.g., "Build a 10x10 oak cabin")
            player_pos: Player position [x, y, z] (optional, uses world spawn if None)
            
        Returns:
            Dict with build status, commands executed, time taken, etc.
        """
        print(f"🏗️ Building: {description}")
        
        # Step 1: Parse description into spatial blueprint
        blueprint = self.analyzer.analyze(description, player_pos)
        print(f"✅ Blueprint generated: {blueprint['structure']}")
        
        # Step 2: Generate Minecraft commands
        commands = self.generator.generate(blueprint)
        print(f"✅ Generated {len(commands)} commands")
        
        # Step 3: Execute on server
        result = self.server.execute_commands(commands)
        print(f"✅ Build complete!")
        
        return {
            "status": "success" if result["executed"] else "failed",
            "description": description,
            "blueprint": blueprint,
            "commands": commands,
            "execution_time": result["execution_time"],
            "blocks_placed": result["blocks_placed"],
            "errors": result.get("errors", [])
        }
    
    def build_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load build description from file and execute."""
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        return self.build(
            description=config["description"],
            player_pos=config.get("player_pos")
        )


if __name__ == "__main__":
    # Example usage
    builder = MinecraftBuilder(
        server_host="localhost",
        server_port=25575,
        rcon_password="your_rcon_password"
    )
    
    result = builder.build("Build a 10x10 oak cabin with a door in front")
    print(json.dumps(result, indent=2))
