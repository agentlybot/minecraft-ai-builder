"""
Server Interface - Minecraft Server Communication

Handles connection and command execution via mcrcon (RCON protocol).
"""

import time
from typing import List, Dict, Any
# Note: mcrcon library to be installed
# pip install mcrcon


class ServerInterface:
    """Interface for Minecraft server command execution"""
    
    def __init__(self, server_host: str, server_port: int, rcon_password: str):
        """
        Initialize server connection (lazy - connects on first command).
        
        Args:
            server_host: IP/hostname (e.g., "localhost" or "192.168.1.100")
            server_port: RCON port (default 25575)
            rcon_password: Server rcon password (set in server.properties)
        """
        self.host = server_host
        self.port = server_port
        self.password = rcon_password
        self.mcr = None
        self._connect_timeout = 10
    
    def _connect(self) -> None:
        """Establish RCON connection"""
        try:
            from mcrcon import MCRcon
            self.mcr = MCRcon(self.host, self.port, self.password)
            self.mcr.connect()
            print(f"✅ Connected to {self.host}:{self.port}")
        except ImportError:
            print("❌ mcrcon not installed. Install with: pip install mcrcon")
            raise
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            raise
    
    def execute_commands(self, commands: List[str], rate_limit: float = 0.05) -> Dict[str, Any]:
        """
        Execute a list of commands on the Minecraft server.
        
        Args:
            commands: List of Minecraft commands to execute
            rate_limit: Delay between commands in seconds (avoid chat flood)
            
        Returns:
            Dict with execution stats
        """
        if not self.mcr:
            self._connect()
        
        results = {
            "executed": 0,
            "failed": 0,
            "execution_time": 0,
            "blocks_placed": 0,
            "errors": []
        }
        
        start_time = time.time()
        
        for i, cmd in enumerate(commands):
            try:
                # Execute command
                response = self.mcr.command(cmd)
                results["executed"] += 1
                
                # Estimate blocks placed (crude heuristic)
                if "/fill" in cmd:
                    # Extract dimensions and estimate
                    parts = cmd.split()
                    try:
                        x1, y1, z1 = int(parts[1]), int(parts[2]), int(parts[3])
                        x2, y2, z2 = int(parts[4]), int(parts[5]), int(parts[6])
                        blocks = abs(x2 - x1 + 1) * abs(y2 - y1 + 1) * abs(z2 - z1 + 1)
                        results["blocks_placed"] += blocks
                    except:
                        results["blocks_placed"] += 1
                else:
                    results["blocks_placed"] += 1
                
                # Rate limiting to prevent chat flood
                if i < len(commands) - 1:
                    time.sleep(rate_limit)
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Command {i}: {str(e)}")
                print(f"❌ Failed to execute: {cmd}")
                print(f"   Error: {e}")
        
        results["execution_time"] = time.time() - start_time
        
        return results
    
    def execute_single(self, command: str) -> str:
        """
        Execute a single command and return response.
        
        Args:
            command: Single Minecraft command
            
        Returns:
            Server response text
        """
        if not self.mcr:
            self._connect()
        
        return self.mcr.command(command)
    
    def get_player_position(self) -> Dict[str, float]:
        """
        Query server for player position.
        
        Returns:
            Dict with x, y, z coordinates
        """
        try:
            response = self.execute_single("/data get entity @s Pos")
            # Parse response and extract coordinates
            # Format: @s has the following entity data: {Pos:[1.5, 65.0, 2.5]}
            # TODO: Implement parsing
            return {"x": 0, "y": 64, "z": 0}
        except:
            return None
    
    def get_inventory(self, player: str = "@s") -> List[Dict[str, Any]]:
        """
        Query player inventory (Phase 2).
        
        Args:
            player: Player name or @s for self
            
        Returns:
            List of items with counts
        """
        # TODO: Implement inventory querying via /data get entity
        pass
    
    def close(self) -> None:
        """Close RCON connection"""
        if self.mcr:
            self.mcr.stop()
            self.mcr = None
            print("❌ Disconnected from server")


if __name__ == "__main__":
    # Example usage (requires running Minecraft server)
    server = ServerInterface(
        server_host="localhost",
        server_port=25575,
        rcon_password="your_password"
    )
    
    try:
        # Test connection
        result = server.execute_single("/say Hello from Minecraft AI Builder!")
        print(f"Response: {result}")
        
        # Test command batch
        commands = [
            "/fill 0 64 0 10 68 10 oak_planks",
            "/setblock 5 64 0 oak_door",
        ]
        result = server.execute_commands(commands)
        print(f"Executed {result['executed']} commands, {result['blocks_placed']} blocks placed")
        
    finally:
        server.close()
