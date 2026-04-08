from pygame import Vector2, Rect
from App.asset_manager import AssetManager
from App.renderer import Sprite2D


class Boat:
    # External Data
    name = "Generic Boat"  # Name
    id = "GenericBoat"  # ID
    cost = 10  # Cost to buy the boat
    texture_id = "boats/boat1_"  # ID for getting the texture for boat. After the _ is team name.
    def __init__(self, team_name: str, position: Vector2, lane: int, asset_manager: AssetManager):
        # Main Data
        self.position: Vector2 = position  # Position (Centered)
        self.rect: Rect = Rect((*position, 100, 35))  # X Y Position, Width, Height
        self.rect_offset: Vector2 = Vector2(0, 25)  # Offset for rect (Applied in self.fix_other_positions)
        self.lane: int = lane  # Which lane (1/2/3) it's on
        self.sprite: Sprite2D = Sprite2D(  # Boat Sprite
            texture=asset_manager.get("textures", f"{self.texture_id}{team_name.upper()}"),  # Get Texture
            position=self.position,  # Sprite should always follow self.position
            position_mode="center",)  # Position Mode. Keep centered.
        self.team_name: str = team_name  # Boat's Team
        self.opponent_team_name: str = self.get_opponent_team_name()
        self.health: int = 100  # Boat's Health
        self.speed: int = 100  # Boat's Speed in px/s calculated by (speed*dt). Can be -/+ Depending on Team
        self.damage: int = 25  # Boat's Damage (When collision, damage is exchanged twice. Technically 25==50DMG)
        self.dead: bool = False  # If the boat is dead or not
        self.won: bool = False  # If the boat has captured the opponent's island (island_health<=0)
        self.fix_direction()  # Fix the Boat's direction immediately
        # Fix rect position to center immediately
        self.fix_other_positions()

    def get_opponent_team_name(self) -> str:  # Get opponent's team name
        return "red" if self.team_name == "blue" else "blue"

    def fix_direction(self):
        # Modify Speed depending on Blue(+)/Red(-) Team
        if self.team_name == "red": self.speed *= -1

    def fix_other_positions(self):
        self.rect.center = self.position  # Center Rect position to self.position
        self.rect.x += self.rect_offset.x  # Apply Rect offset
        self.rect.y += self.rect_offset.y  # Apply Rect offset
        self.sprite.position = self.position  # Set Sprite position to self.position

    def kill(self):
        # Set self to dead
        self.dead = True
        # Wait for the Game Manager to clean up this boat, and summon an explosion

    def win(self):
        self.won = True
        # Wait for the Game Manager to clean up this boat, and execute Win for ____ Team

    def update_basic(self, dt: float, teams, team_edges: dict[str, int]):
        if not self.dead:
            # Move the Boat
            self.position.x += self.speed * dt
            # Center the Rect
            self.fix_other_positions()
            # Check who is the opposite team
            if self.team_name == "blue":  # Red is the enemy
                enemy_boats_list: list = teams.red.boats
            else:  # Blue is the enemy
                enemy_boats_list: list = teams.blue.boats
            # Check Collisions on the opposite team
            for boat in enemy_boats_list:
                # If collided and the boat is alive and on the same lane
                if self.rect.colliderect(boat) and not boat.dead and boat.lane == self.lane:
                    # Exchange damage with each other
                    boat.health -= self.damage
                    self.health -= boat.damage
            # Check Health, if <=0 then kill itself (D:)
            if self.health <= 0:
                self.kill()
            # Check if it reached the opponent's island
            if self.team_name == "blue" and self.position.x >= team_edges["red"]:
                # If it reaches the Island, deal damage then die
                teams.red.island_health -= self.damage
                self.kill()
                # Check if the Island has <= 0 health. If so, set off a Win so the Game Manager can clean up
                if teams.red.island_health <= 0:
                    self.win()
            elif self.team_name == "red" and self.position.x <= team_edges["blue"]:
                # If it reaches the Island, deal damage then die
                teams.blue.island_health -= self.damage
                self.kill()
                # Check if the Island has <= 0 health, then win if so
                if teams.blue.island_health <= 0:
                    self.win()

    def update(self, dt: float, teams, team_edges: dict[str, int]):
        self.update_basic(dt, teams, team_edges)

    def draw(self, renderer, debug_mode=False):
        # Draw Sprite
        renderer.draw_sprite(self.sprite)
        if debug_mode:  # Is debug?
            # Draw Debug Hitbox
            if self.team_name == "blue":
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)
            renderer.draw_rect(self.rect, color=(*color, 100))
