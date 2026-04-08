from dataclasses import dataclass, field
from pygame import Vector2, Rect
from App.renderer import Renderer, Texture2D
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.input import InputManager
from World.background import Background
from Entities.boats import Boat
from Entities.explosion import Explosion
from App.boat_loader import load_boats
from App.ui import UIRadioButtonGroup, UIRadioButton, UILabel
from App.clock import Timer
from App.controllers import BlueController, RedController


# The actual Gameplay part of the Game
class InGame:
    def __init__(self,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager):
        # Set Managers
        self.renderer: Renderer = renderer
        self.asset_manager: AssetManager = asset_manager
        self.mixer: Mixer = mixer
        self.input_manager: InputManager = input_manager
        self.background = Background(self.renderer, self.asset_manager)
        # Load Boats
        self.boat_registry: dict = load_boats()
        # Set States
        self.running: bool = False
        # Declare Teams
        self.teams: Teams | None = None
        # Declare Objects (Explosions, Cannonballs, Mines, etc)
        self.explosions: list[Explosion] | None = None
        self.cannonballs: list | None = None
        self.mines: list | None = None
        # Declare Constants
        self.TEAM_BOAT_EDGE_X: dict[str, int] = {  # Team Boat Spawn/Win X positions
            "blue": 200,
            "red": 1080,
        }
        self.LANE_LEVEL_Y: dict[int, int] = {  # Y level for each Lane (To spawn boats in)
            1: 870,
            2: 930,
            3: 990,
        }
        self.BOAT_SELECTOR: dict = {
            "blue_start_x": 100,
            "red_start_x": 1180,
            "button_space": 74,
            "boundary": Rect(0, 450, 1280, 720+480),
        }
        self.lanes = Lanes()
        # Init Boat Selector
        self.boat_selector_blue = UIRadioButtonGroup("Speed Boat", self.renderer)
        self.boat_selector_red = UIRadioButtonGroup("Speed Boat", self.renderer)
        self.setup_boat_selection_ui()
        # New Game
        self.new(False)

    def setup_boat_selection_ui(self):
        i = 0
        for boat_class in self.boat_registry.values():
            i += 1
            print("Loaded:", boat_class)
            print("-", boat_class.name)
            print("-", boat_class.cost)
            print("-", boat_class.texture_id)
            self.boat_selector_blue.add(boat_class.name,
                                        UIRadioButton(
                                            self.renderer,
                                            self.asset_manager,
                                            self.mixer,
                                            self.input_manager,
                                            (
                                                self.BOAT_SELECTOR["blue_start_x"] + i * self.BOAT_SELECTOR["button_space"],
                                                1130, 64, 64),
                                            None,
                                            f"{boat_class.texture_id}BLUE",
                                            UILabel(
                                                Vector2(0, 0),  # Set inside init
                                                f"${boat_class.cost}",
                                                self.renderer,
                                                self.asset_manager,
                                                self.mixer,
                                                self.input_manager,
                                            ),
                                            position_mode="center",
                                            use_camera=True,
                                        )
            )
            self.boat_selector_blue[boat_class.name].id = boat_class.id
            self.boat_selector_red.add(boat_class.name,
                                        UIRadioButton(
                                            self.renderer,
                                            self.asset_manager,
                                            self.mixer,
                                            self.input_manager,
                                            (
                                                self.BOAT_SELECTOR["red_start_x"] - i * self.BOAT_SELECTOR["button_space"],
                                                1130, 64, 64),
                                            None,
                                            f"{boat_class.texture_id}RED",
                                            UILabel(
                                                Vector2(0, 0),  # Set inside init
                                                f"${boat_class.cost}",
                                                self.renderer,
                                                self.asset_manager,
                                                self.mixer,
                                                self.input_manager,
                                            ),
                                            position_mode="center",
                                            use_camera=True,
                                        )
            )
            self.boat_selector_red[boat_class.name].id = boat_class.id

    # Start a new game
    def new(self, start=True):
        # Set Teams
        self.teams = Teams(Team("blue", PlayerCursor("blue",
                                                     Vector2(200, 800),
                                                     BlueController(self.input_manager),
                                                     self.asset_manager)),
                           Team("red", PlayerCursor("red",
                                                    Vector2(1080, 800),
                                                    RedController(self.input_manager),
                                                    self.asset_manager)))
        # Set Objects (Explosions, Cannonballs, Mines, etc)
        self.explosions = []
        self.cannonballs = []
        self.mines = []
        # Start the Game if said so
        if start:
            self.unpause()

    def add_boat(self, team: str, boat: str, lane: int):
        if team == "blue":  # In Blue team
            self.teams.blue.boats.append(self.boat_registry[boat]("blue",
                                              Vector2(self.TEAM_BOAT_EDGE_X["blue"], self.LANE_LEVEL_Y[lane]), lane,
                                              self.asset_manager))
            self.teams.blue.money -= self.boat_registry[boat].cost
            self.teams.blue.cursor.wait()
        else:  # In Red Team
            self.teams.red.boats.append(self.boat_registry[boat]("red",
                                             Vector2(self.TEAM_BOAT_EDGE_X["red"], self.LANE_LEVEL_Y[lane]), lane,
                                             self.asset_manager))
            self.teams.red.money -= self.boat_registry[boat].cost
            self.teams.red.cursor.wait()

    def unpause(self): self.running = True  # Unpauses the game

    def pause(self): self.running = False  # Pauses the game

    def update_money(self, dt):  # Update Money
        self.teams.blue.money += self.teams.blue.money_base_increase * self.teams.blue.money_multiplier * dt
        self.teams.red.money += self.teams.red.money_base_increase * self.teams.red.money_multiplier * dt

    def update(self, dt):
        # Update Background (Sky, Sea, Islands, Lanes animation)
        self.background.update(dt)

        # Update Game Objects
        if self.running:
            # Update Money
            self.update_money(dt)

            # Update cursors
            self.teams.blue.cursor.update(dt)
            self.teams.red.cursor.update(dt)

            # Update Boat Selectors
            selected_blue = self.boat_selector_blue.update(dt, self.teams.blue.cursor, # Blue
                                                           self.renderer.main_camera)
            if selected_blue:
                self.teams.blue.cursor.selected_item = selected_blue.id

            selected_red = self.boat_selector_red.update(dt, self.teams.red.cursor,  # Red
                                                         self.renderer.main_camera)
            if selected_red:
                self.teams.red.cursor.selected_item = selected_red.id

            # Update Lanes placement Checks

            blue_cursor = self.teams.blue.cursor
            blue_clicked = blue_cursor.has_normal_click()

            if blue_cursor.status == "normal" and blue_clicked:
                blue_pos = blue_cursor.position

                if self.lanes.one.rect.collidepoint(blue_pos):  # Blue Place Lane 1
                    if self.teams.blue.money >= self.boat_registry[blue_cursor.selected_item].cost:
                        self.add_boat("blue", blue_cursor.selected_item, 1)
                    else:  # They aren't rich enough
                        blue_cursor.poor()
                elif self.lanes.two.rect.collidepoint(blue_pos):  # Blue Place Lane 2
                    if self.teams.blue.money >= self.boat_registry[blue_cursor.selected_item].cost:
                        self.add_boat("blue", blue_cursor.selected_item, 2)
                    else:  # They aren't rich enough
                        blue_cursor.poor()
                elif self.lanes.three.rect.collidepoint(blue_pos):  # Blue Place Lane 3
                    if self.teams.blue.money >= self.boat_registry[blue_cursor.selected_item].cost:
                        self.add_boat("blue", blue_cursor.selected_item, 3)
                    else:  # They aren't rich enough
                        blue_cursor.poor()

            red_cursor = self.teams.red.cursor
            red_clicked = red_cursor.has_normal_click()

            if red_cursor.status == "normal" and red_clicked:
                red_pos = red_cursor.position

                if self.lanes.one.rect.collidepoint(red_pos):  # Red Place Lane 1
                    if self.teams.red.money >= self.boat_registry[red_cursor.selected_item].cost:
                        self.add_boat("red", red_cursor.selected_item, 1)
                    else:  # They aren't rich enough
                        red_cursor.poor()
                elif self.lanes.two.rect.collidepoint(red_pos):  # Red Place Lane 2
                    if self.teams.red.money >= self.boat_registry[red_cursor.selected_item].cost:
                        self.add_boat("red", red_cursor.selected_item, 2)
                    else:  # They aren't rich enough
                        red_cursor.poor()
                elif self.lanes.three.rect.collidepoint(red_pos):  # Red Place Lane 3
                    if self.teams.red.money >= self.boat_registry[red_cursor.selected_item].cost:
                        self.add_boat("red", red_cursor.selected_item, 3)
                    else:  # They aren't rich enough
                        red_cursor.poor()

            # Loop through all boats to update them
            for boat in self.teams.red.boats + self.teams.blue.boats:
                boat.update(dt, self.teams, self.TEAM_BOAT_EDGE_X)

            # Loop through all boats to clean them up
            for boat in self.teams.red.boats + self.teams.blue.boats:
                if boat.dead:
                    if boat.team_name == "blue":  # If Blue
                        # Summon Explosion
                        self.explosions.append(Explosion(boat.position, self.asset_manager))
                        self.teams.blue.boats.remove(boat)
                    elif boat.team_name == "red":  # If Red
                        # Summon Explosion
                        self.explosions.append(Explosion(boat.position, self.asset_manager))
                        self.teams.red.boats.remove(boat)

            # Loop through all explosions to update them
            for explosion in self.explosions:
                explosion.update(dt)

    def draw(self, debug_mode=False):
        # Draw Background in the back
        self.background.draw_all()

        # Draw (Debug) Lanes
        if debug_mode:
            self.renderer.draw_rect(
                self.lanes.one.rect,
                self.lanes.one.color
            )
            self.renderer.draw_rect(
                self.lanes.two.rect,
                self.lanes.two.color
            )
            self.renderer.draw_rect(
                self.lanes.three.rect,
                self.lanes.three.color
            )

        # Draw Boats
        for lane in (1, 2, 3):
            for boat in self.teams.red.boats + self.teams.blue.boats:
                if boat.lane == lane:
                    boat.draw(self.renderer, debug_mode)

        # Draw Explosions
        for explosion in self.explosions:
            explosion.draw(self.renderer, debug_mode)

        # Draw Boat Selector UI
        self.boat_selector_blue.draw_all()
        self.boat_selector_red.draw_all()

        # Draw the Island Health bars

        # Blue Health Bar
        self.renderer.draw_rect(  # HB BG
            Rect(8, 748, 104, 14),
            (0, 0, 0, 100)
        )
        self.renderer.draw_rect(  # HB FG
            Rect(10, 750, max(0, self.teams.blue.island_health), 10),
            (0, 0, 255, 200)
        )
        # Red Health Bar
        self.renderer.draw_rect(  # HB BG
            Rect(1168, 748, 104, 14),
            (0, 0, 0, 100)
        )
        self.renderer.draw_rect(  # HB FG
            Rect(1170, 750, max(0, self.teams.red.island_health), 10),
            (255, 0, 0, 200)
        )

        # Draw Cursors
        if self.running:  # Only draw when In-Game
            self.teams.blue.cursor.draw(self.renderer)
            self.teams.red.cursor.draw(self.renderer)


class PlayerCursor:
    def __init__(self, team: str, position: Vector2, controller, asset_manager: AssetManager):
        self.team = team  # Set Team
        self.position: Vector2 = Vector2(position)
        # Set Textures
        self.texture_normal: Texture2D = asset_manager.get("textures", f"cursor/{self.team}")
        self.texture_loading0: Texture2D = asset_manager.get("textures", f"cursor/{self.team}_0")
        self.texture_loading1: Texture2D = asset_manager.get("textures", f"cursor/{self.team}_1")
        self.texture_loading2: Texture2D = asset_manager.get("textures", f"cursor/{self.team}_2")
        self.texture_loading3: Texture2D = asset_manager.get("textures", f"cursor/{self.team}_3")
        self.texture_loading4: Texture2D = asset_manager.get("textures", f"cursor/{self.team}_4")
        self.loading_animation = [
            self.texture_loading0, self.texture_loading1, self.texture_loading2,
            self.texture_loading3, self.texture_loading4
        ]
        self.texture_poor: Texture2D = asset_manager.get("textures", f"cursor/{self.team}_poor")
        self.status = "normal"  # normal, loading, poor
        self.texture: Texture2D = self.texture_normal  # Set current texture to Normal
        self.loading_animation_frame = 0  # Set Loading Animation Frame
        self.controller = controller
        self._prev_click = False
        self._just_clicked = False
        self.selected_item = "SpeedBoat"
        # Set Timers
        self.loading_animation_timer = Timer(0.1, start=False, repeat=False)  # Set repeat when reset
        self.poor_timer = Timer(1, start=False, repeat=False)
        # Set Constant
        self.SPEED = 350

    def clear_statuses(self):
        self.loading_animation_timer = Timer(0.1, start=False, repeat=False)  # Set repeat when reset
        self.poor_timer = Timer(1, start=False, repeat=False)
        self.loading_animation_frame = 0
        self.texture = self.texture_normal
        self.status = "normal"

    def wait(self):
        self.loading_animation_timer.repeat = True
        self.loading_animation_timer.reset()
        self.loading_animation_frame = 0
        self.texture = self.texture_loading0
        self.status = "loading"

    def poor(self):
        self.poor_timer.reset()
        self.texture = self.texture_poor
        self.status = "poor"

    def has_normal_click(self) -> bool:
        return self._just_clicked

    def update(self, dt):
        # Change status when timer activates
        if self.poor_timer.update(dt):  # If poor Timer ends
            self.clear_statuses()
        if self.loading_animation_timer.update(dt):  # If animation flip
            self.loading_animation_frame += 1  # Increment frame by 1
            if self.loading_animation_frame >= len(self.loading_animation):  # If there are no more frames
                self.clear_statuses()
            else:
                self.texture = self.loading_animation[self.loading_animation_frame]  # Update Frame
        # Check Movement/Click input
        movement = self.controller.get_movement()
        self.position += movement * self.SPEED * dt  # Update position

        # Detect NORMAL Click
        current_click = self.controller.get_click()
        self._just_clicked = current_click and not self._prev_click
        self._prev_click = current_click

    def draw(self, renderer: Renderer):
        # Draw Cursor
        renderer.draw_texture(
            self.texture,
            self.position + (Vector2(-8, 0) if self.status == "normal" else Vector2(0, 0)),
            position_mode="center")  #  ^ Fix the loading animation centering problem


@dataclass
class Team:
    name: str
    cursor: PlayerCursor
    money: int = 80
    money_base_increase: int = 10  # $/ps
    money_multiplier: float = 1.0
    boats: list[Boat] = field(default_factory=list)
    island_health: int = 100


@dataclass
class Teams:
    blue: Team
    red: Team


@dataclass
class Lane:
    rect: Rect
    color: tuple[int, int, int, int]

@dataclass
class Lanes:
    one: Lane = field(default_factory=lambda: Lane(Rect(105, 870, 1055, 65), (100, 0, 0, 100)))
    two: Lane = field(default_factory=lambda: Lane(Rect(105, 935, 1055, 65), (0, 100, 0, 100)))
    three: Lane = field(default_factory=lambda: Lane(Rect(105, 1000, 1055, 65), (0, 0, 100, 100)))
