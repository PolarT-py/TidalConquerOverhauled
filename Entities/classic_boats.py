from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.renderer import Sprite2D
from Entities.boats import Boat
from Entities.projectiles import CannonBall
from App.clock import Timer


class SpeedBoat(Boat):
    # External Data
    name = "Speed Boat"  # Name
    id = "SpeedBoat"  # ID
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
        self.health_max: int = 100  # Boat's Max Health
        self.health: int = self.health_max  # Boat's Health
        self.speed: int = 70  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 25  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
        self.fix_direction()  # Fix the Boat's direction immediately


class TankBoat(Boat):
    # External Data
    name = "Tank Boat"  # Name
    id = "TankBoat"  # ID
    cost = 50  # Cost to buy the boat
    texture_id = "boats/boat2_"  # ID for getting the texture for boat. After the _ is team name.
    def __init__(self, team_name: str, position: Vector2, lane: int, asset_manager: AssetManager):
        super().__init__(team_name, position, lane, asset_manager)
        # Main Data
        self.position: Vector2 = position  # Position (Centered)
        self.rect: Rect = Rect((*position, 110, 36))  # X Y Position, Width, Height
        self.rect_offset: Vector2 = Vector2(0, 22)  # Offset for rect (Applied in self.fix_other_positions)
        self.texture_offset: Vector2 = Vector2(0, 0)  # Offset for texture rendering
        self.lane: int = lane  # Which lane (1/2/3) it's on
        self.sprite: Sprite2D = Sprite2D(  # Boat Sprite
            texture=asset_manager.get("textures", f"{self.texture_id}{team_name.upper()}"),  # Get Texture
            position=self.position,  # Sprite should always follow self.position
            position_mode="center",)  # Position Mode. Keep centered.
        self.health_max: int = 300  # Boat's Max Health
        self.health: int = self.health_max  # Boat's Health
        self.speed: int = 40  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 25  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
        self.fix_direction()  # Fix the Boat's direction immediately



class CannonBoat(Boat):
    # External Data
    name = "Cannon Boat"  # Name
    id = "CannonBoat"  # ID
    cost = 80  # Cost to buy the boat
    texture_id = "boats/boat3_"  # ID for getting the texture for boat. After the _ is team name.
    def __init__(self, team_name: str, position: Vector2, lane: int, asset_manager: AssetManager):
        super().__init__(team_name, position, lane, asset_manager)
        # Main Data
        self.position: Vector2 = position  # Position (Centered)
        self.rect: Rect = Rect((*position, 120, 55))  # X Y Position, Width, Height
        self.rect_offset: Vector2 = Vector2(0, 15)  # Offset for rect (Applied in self.fix_other_positions)
        self.texture_offset: Vector2 = Vector2(0, -18)  # Offset for texture rendering
        self.lane: int = lane  # Which lane (1/2/3) it's on
        self.sprite: Sprite2D = Sprite2D(  # Boat Sprite
            texture=asset_manager.get("textures", f"{self.texture_id}{team_name.upper()}"),  # Get Texture
            position=self.position,  # Sprite should always follow self.position
            position_mode="center",)  # Position Mode. Keep centered.
        self.health_max: int = 200  # Boat's Max Health
        self.health: int = self.health_max  # Boat's Health
        self.speed: int = 30  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 50  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
        self.fix_direction()  # Fix the Boat's direction immediately
        # Some fun exclusive stuff
        self.shoot_timer: Timer = Timer(2.5, start=True, repeat=True)  # Shoot every 2.5 seconds
        self.shoot_timer.time_left = 1.0  # Instantly shoot when spawn
        self.shoot_position_offset: Vector2 = Vector2(35 if self.team_name == "blue" else -35,
                                                      -35)  # Offset to a more preferred position

    def update(self, dt: float, teams, team_edges, asset_manager=None, mixer=None):
        self.update_basic(dt, teams, team_edges)  # BORING necessary basic stuff
        # Shooting updated outside

    def update_shooting(self, dt, asset_manager, mixer):
        # Shooting
        if self.shoot_timer.update(dt) and asset_manager is not None:  # Can shoot
            mixer.play_sound("effects/cannonboom")
            return CannonBall(self.position + self.shoot_position_offset,
                                               160 if self.speed > 0 else -160, -140,
                                               self.position.y + 40,
                                               self.team_name, self.lane, asset_manager)
        return None
