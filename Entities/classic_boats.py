from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.renderer import Sprite2D
from Entities.boats import Boat


class Boat1(Boat):
    # External Data
    name = "Speed Boat"  # Name
    cost = 20  # Cost to buy the boat
    texture_id = "boats/boat1_"  # ID for getting the texture for boat. After the _ is team name.
    def __init__(self, team_name: str, position: Vector2, lane: int, asset_manager: AssetManager):
        super().__init__(team_name, position, lane, asset_manager)
        # Main Data
        self.position: Vector2 = position  # Position (Centered)
        self.rect: Rect = Rect((*position, 100, 35))  # X Y Position, Width, Height
        self.rect_offset: Vector2 = Vector2(0, 25)  # Offset for rect (Applied in self.fix_other_positions)
        self.lane: int = lane  # Which lane (1/2/3) it's on
        self.sprite: Sprite2D = Sprite2D(  # Boat Sprite
            texture=asset_manager.get("textures", f"{self.texture_id}{team_name.upper()}"),  # Get Texture
            position=self.position,  # Sprite should always follow self.position
            position_mode="center",)  # Position Mode. Keep centered.
        self.health: int = 100  # Boat's Health
        self.speed: int = 75  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 25  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
