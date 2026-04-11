from dataclasses import dataclass, field
from pygame import Vector2, Rect
from App.renderer import Renderer, Texture2D
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.input import InputManager
from App.settings import Settings
from World.background import Background
from Entities.boats import Boat
from Entities.classic_boats import CannonBoat, TrapperBoat
from Entities.tco_boats import ExplosiveBoat
from Entities.explosion import Explosion, BlueExplosion, RedExplosion
from Entities.projectiles import CannonBall, Trap
from App.boat_loader import load_boats
from App.ui import UIRadioButtonGroup, UIRadioButton, UILabel, UITextureButton
from App.clock import Timer
from App.controllers import BlueController, RedController
from App.debug import debug_print


# The actual Gameplay part of the Game
class InGame:
    def __init__(self,
                 renderer: Renderer,
                 asset_manager: AssetManager,
                 mixer: Mixer,
                 input_manager: InputManager,
                 settings: Settings):
        # Cool Variables
        self.uptime = 0
        # Set Managers
        self.renderer: Renderer = renderer
        self.asset_manager: AssetManager = asset_manager
        self.mixer: Mixer = mixer
        self.input_manager: InputManager = input_manager
        self.settings: Settings = settings
        self.background = Background(self.renderer, self.asset_manager)
        # Load Boats
        self.boat_registry: dict = load_boats()
        # Set States
        self.running: bool = False  # Is running
        self.debug_mode: bool = False  # Changed in game.py
        # Declare Teams
        self.teams: Teams | None = None
        # Declare Objects (Explosions, Cannonballs, Mines, etc)
        self.explosions: list[Explosion] | None = None  # Explosions
        self.cannonballs: list[CannonBall] | None = None  # Cannonballs that have been orphaned
        self.traps: list[Trap] | None = None  # Traps that have been orphaned
        # Declare Constants
        self.TEAM_BOAT_EDGE_X: dict[str, int] = {  # Team Boat Spawn/Win X positions
            "blue": 200,
            "blue_hit": 160,
            "red": 1080,
            "red_hit": 1120,
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
            "boundary": Rect(16, 458, 1280, 720+480-38),
        }
        self.lanes = Lanes()
        # Init Boat Selector
        self.boat_selector_blue = UIRadioButtonGroup("Speed Boat", self.renderer)
        self.boat_selector_red = UIRadioButtonGroup("Speed Boat", self.renderer)
        self.setup_boat_selection_ui()
        # Init Timers
        self.eco_unlock_timer: Timer | None = None
        # Init Team Upgrades
        # Desktop
        if self.settings.main.platform == "Desktop":
            self.money_upgrade_blue = UITextureButton(self.renderer, self.asset_manager,
                                                      self.mixer, self.input_manager,
                                                      (32, 1138, 50, 50),
                                                      self.asset_manager.get("textures",
                                                                             "buttons/money_upgrade_button"),
                                                      use_camera=True, position_mode="center",
                                                      enabled=False)
            self.money_upgrade_red = UITextureButton(self.renderer, self.asset_manager,
                                                      self.mixer, self.input_manager,
                                                      (1248, 1138, 50, 50),
                                                      self.asset_manager.get("textures",
                                                                             "buttons/money_upgrade_button"),
                                                      use_camera=True, position_mode="center",
                                                     enabled=False)
            self.money_upgrade_blue_label = UILabel(Vector2(32, 1105), "$69",
                                                    self.renderer, self.asset_manager,
                                                    self.mixer, self.input_manager,
                                                    use_camera=True, position_mode="center",
                                                    text_font=self.asset_manager.get("fonts",
                                                                                     "PirataOne"))
            self.money_upgrade_red_label = UILabel(Vector2(1248, 1105), "$69",
                                                    self.renderer, self.asset_manager,
                                                    self.mixer, self.input_manager,
                                                    use_camera=True, position_mode="center",
                                                    text_font=self.asset_manager.get("fonts",
                                                                                    "PirataOne"))
        else:  # Mobile
            self.money_upgrade_blue = UITextureButton(
                self.renderer, self.asset_manager,
                self.mixer, self.input_manager,
                (32 + 20, 1138 - 13, 80, 80),
                self.asset_manager.get("textures", "buttons/money_upgrade_button"),
                use_camera=True, position_mode="center",
                enabled=False, scale=Vector2(1.6, 1.6)
            )

            self.money_upgrade_red = UITextureButton(
                self.renderer, self.asset_manager,
                self.mixer, self.input_manager,
                (1248 - 20, 1138 - 13, 80, 80),
                self.asset_manager.get("textures", "buttons/money_upgrade_button"),
                use_camera=True, position_mode="center",
                enabled=False, scale=Vector2(1.6, 1.6)
            )

            self.money_upgrade_blue_label = UILabel(
                Vector2(32 + 20, 1105 - 30), "$69",
                self.renderer, self.asset_manager,
                self.mixer, self.input_manager,
                use_camera=True, position_mode="center", text_size=48,
                text_font=self.asset_manager.get("fonts", "PirataOne")
            )

            self.money_upgrade_red_label = UILabel(
                Vector2(1248 - 20, 1105 - 30), "$69",
                self.renderer, self.asset_manager,
                self.mixer, self.input_manager,
                use_camera=True, position_mode="center", text_size=48,
                text_font=self.asset_manager.get("fonts", "PirataOne")
            )
        # New Game
        self.new(False)

    def setup_boat_selection_ui(self):
        i = 0
        boat_classes = sorted(  # Sorted by cost
            self.boat_registry.values(),
            key=lambda cls: cls.cost
        )
        for boat_class in boat_classes:
            i += 1
            debug_print(f"Loaded: {boat_class}", self.debug_mode)
            debug_print(f"- {boat_class.name}", self.debug_mode)
            debug_print(f"- {boat_class.cost}", self.debug_mode)
            debug_print(f"- {boat_class.texture_id}", self.debug_mode)
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
                                            scale=boat_class.scale,
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
                                            scale=boat_class.scale,
                                            position_mode="center",
                                            use_camera=True,
                                        )
            )
            self.boat_selector_red[boat_class.name].id = boat_class.id

    # Start a new game
    def new(self, start=True):
        # Cool Variables
        self.uptime = 0
        # Set Teams
        self.teams = Teams(Team("blue", PlayerCursor("blue",
                                                     Vector2(200, 800),
                                                     BlueController(self.input_manager),
                                                     self.BOAT_SELECTOR["boundary"],
                                                     self.asset_manager)),
                           Team("red", PlayerCursor("red",
                                                    Vector2(1080, 800),
                                                    RedController(self.input_manager),
                                                    self.BOAT_SELECTOR["boundary"],
                                                    self.asset_manager)))
        # Set Objects (Explosions, Cannonballs, Mines, etc)
        self.explosions: list[Explosion] = []
        self.cannonballs: list[CannonBall] = []
        self.traps: list[Trap] = []
        # Reset Boat Selector Default Option
        self.boat_selector_blue.select("Speed Boat")
        self.boat_selector_red.select("Speed Boat")
        # Reset Eco unlock Timer
        self.eco_unlock_timer: Timer = Timer(self.teams.blue.eco_unlock_time, start=True)  # Eco unlock time same for all teams
        # Reset Eco to lock
        self.money_upgrade_blue.enabled = False
        self.money_upgrade_red.enabled = False
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
        self.mixer.play_sound("effects/build")

    def unpause(self): self.running = True  # Unpauses the game

    def pause(self): self.running = False  # Pauses the game

    def update_money(self, dt):  # Update Money
        # Increase the money
        self.teams.blue.money += self.teams.blue.money_base_increase * dt
        self.teams.red.money += self.teams.red.money_base_increase * dt
        # Cap the money if too much
        if self.teams.blue.money > self.teams.blue.money_cap:
            self.teams.blue.money = self.teams.blue.money_cap
        if self.teams.red.money > self.teams.red.money_cap:
            self.teams.red.money = self.teams.red.money_cap

    def update(self, dt):
        # Update Background (Sky, Sea, Islands, Lanes animation)
        self.background.update(dt)

        # Update Game Objects
        if self.running:
            # Update Uptime Time
            self.uptime += dt
            # Update Money
            self.update_money(dt)

            # Set Eco to unlock once Timer finished
            if self.eco_unlock_timer.update(dt):
                self.teams.blue.eco_unlocked = True
                self.teams.red.eco_unlocked = True
                self.money_upgrade_blue.enabled = True
                self.money_upgrade_red.enabled = True
                self.mixer.play_sound("effects/coin")

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

            # Update Upgrade Money Buttons
            blue_money_upgrade_bought = self.money_upgrade_blue.update(dt, custom_cursor=self.teams.blue.cursor,
                                           camera=self.renderer.main_camera)
            if blue_money_upgrade_bought and\
                self.teams.blue.money >= self.teams.blue.money_increase_buy_price and\
                    self.teams.blue.eco_unlocked:  # Blue Bought an upgrade
                # Take away the money
                self.teams.blue.money -= self.teams.blue.money_increase_buy_price
                # Increase Team's money/second
                self.teams.blue.money_base_increase += self.teams.blue.money_base_increase_grow_amount
                # Make upgrade buy price higher
                self.teams.blue.money_increase_buy_price += self.teams.blue.money_increase_buy_price_grow_amount
                self.mixer.play_sound("effects/coin")
            red_money_upgrade_bought = self.money_upgrade_red.update(dt, custom_cursor=self.teams.red.cursor,
                                           camera=self.renderer.main_camera)
            if red_money_upgrade_bought and\
                self.teams.red.money >= self.teams.red.money_increase_buy_price and\
                    self.teams.red.eco_unlocked:  # Red Bought an upgrade
                # Take away the money
                self.teams.red.money -= self.teams.red.money_increase_buy_price
                # Increase Team's money/second
                self.teams.red.money_base_increase += self.teams.red.money_base_increase_grow_amount
                # Make upgrade buy price higher
                self.teams.red.money_increase_buy_price += self.teams.red.money_increase_buy_price_grow_amount
                self.mixer.play_sound("effects/coin")
            # Update the Upgrade Money Labels
            self.money_upgrade_blue_label.text.content = f"${self.teams.blue.money_increase_buy_price}"
            self.money_upgrade_blue_label.update(dt)
            self.money_upgrade_red_label.text.content = f"${self.teams.red.money_increase_buy_price}"
            self.money_upgrade_red_label.update(dt)

            # Update Lanes placement Checks

            # Get mouse pos
            virtual_mouse_pos = self.input_manager.mouse_pos_virtual
            if virtual_mouse_pos is not None:
                mouse_pos = virtual_mouse_pos - self.renderer.main_camera.offset
            else:
                mouse_pos = Vector2(-10000000000, -10000000000)

            blue_cursor = self.teams.blue.cursor
            blue_cursor_triggered = blue_cursor.status == "normal" and blue_cursor.has_hold()
            blue_mouse_triggered = (
                    mouse_pos is not None
                    and self.input_manager.is_mouse_down(1)
                    and mouse_pos.x < 640 and blue_cursor.status == "normal"
            )
            # Check mouse and playerCursor triggers
            if blue_cursor_triggered:
                blue_pos = blue_cursor.position
            elif blue_mouse_triggered:
                blue_pos = mouse_pos
            else:
                blue_pos = None
            # Check which Lane is clicked
            if blue_pos is not None:
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
            red_cursor_triggered = red_cursor.status == "normal" and red_cursor.has_hold()
            red_mouse_triggered = (
                    mouse_pos is not None
                    and self.input_manager.is_mouse_down(1)
                    and mouse_pos.x >= 640 and red_cursor.status == "normal"
            )
            # Check mouse and playerCursor triggers
            if red_cursor_triggered:
                red_pos = red_cursor.position
            elif red_mouse_triggered:
                red_pos = mouse_pos
            else:
                red_pos = None
            # Check which Lane is clicked
            if red_pos is not None:
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

            # Loop through all Cannonballs to update them
            for cannonball in self.cannonballs:
                cannonball.update(dt)
                if cannonball.dead:
                    self.cannonballs.remove(cannonball)
            # Loop through all Traps to update them
            for trap in self.traps:
                trap.update(dt)
                if trap.dead:
                    self.traps.remove(trap)

            # Loop through all boats to update them
            for boat in self.teams.red.boats + self.teams.blue.boats:
                boat.update(dt, self.teams, self.TEAM_BOAT_EDGE_X, self.asset_manager, self.mixer)
                if "shooting" in boat.abilities:
                    boat: CannonBoat = boat
                    shoot = boat.update_shooting(dt, self.asset_manager, self.mixer)
                    if shoot is not None:
                        self.cannonballs.append(shoot)
                if "trapping" in boat.abilities:
                    boat: TrapperBoat = boat
                    trap = boat.update_trapping(dt, self.asset_manager, self.mixer)
                    if trap is not None:
                        self.traps.append(trap)

            # Loop through all boats to clean them up
            for boat in self.teams.red.boats + self.teams.blue.boats:
                # Cannonball Collision
                for cannonball in self.cannonballs:  # See cannonball collision
                    if cannonball.rect.colliderect(boat.rect) and not cannonball.despawn:  # Cannonball hit
                        if cannonball.team != boat.team_name and\
                            cannonball.lane == boat.lane:  # Prevent friendly fire and only hit in the same lane
                            self.explosions.append(Explosion(boat.position, self.asset_manager))
                            self.mixer.play_sound("effects/break")
                            boat.health -= cannonball.damage
                            if boat.health <= 0: boat.kill()
                            cannonball.kill()
                # Trap Collision
                for trap in self.traps:  # See trap collision
                    if trap.rect.colliderect(boat.rect) and not trap.despawn and trap.landed:  # Trap hit
                        if trap.team != boat.team_name and\
                            trap.lane == boat.lane:  # Prevent friendly fire and only hit in the same lane
                            self.explosions.append(Explosion(boat.position, self.asset_manager))
                            self.explosions.append(Explosion(trap.position, self.asset_manager))
                            self.mixer.play_sound("effects/break")
                            boat.health -= trap.damage
                            if boat.health <= 0: boat.kill()
                            trap.kill()
                if boat.dead:  # If dead
                    if "explosive" in boat.abilities:  # If it has the explosive ability
                        boat: ExplosiveBoat = boat  # Set Class
                        if boat.can_explode:
                            # Summon Explosions in radius
                            self.explosions.append(Explosion(boat.position + Vector2(80, 0), self.asset_manager, wait_time=0.05))
                            self.explosions.append(Explosion(boat.position - Vector2(80, 0), self.asset_manager, wait_time=0.05))
                            self.explosions.append(Explosion(boat.position + Vector2(200, 0), self.asset_manager, wait_time=0.15))
                            self.explosions.append(Explosion(boat.position - Vector2(200, 0), self.asset_manager, wait_time=0.15))
                            # Apply range damage to enemies in the same lane
                            for opponent_boat in self.teams.blue.boats + self.teams.red.boats:  # In all boats
                                if opponent_boat.team_name == boat.opponent_team_name:  # If enemy (Apply full damage)
                                    if opponent_boat.lane == boat.lane:  # If same lane
                                        distance = abs(opponent_boat.position.x - boat.position.x)
                                        if distance <= boat.close_hurt_radius:
                                            opponent_boat.health -= boat.close_damage
                                        elif distance <= boat.near_hurt_radius:
                                            opponent_boat.health -= boat.near_damage
                                        elif distance <= boat.far_hurt_radius:
                                            opponent_boat.health -= boat.far_damage
                                        if opponent_boat.health <= 0: opponent_boat.kill()
                                elif opponent_boat.team_name == boat.team_name:  # If Friendly (Apply halved damage) (Sorry bad variable naming lol)
                                    if opponent_boat.lane == boat.lane:  # If same lane
                                        distance = abs(opponent_boat.position.x - boat.position.x)
                                        if distance <= boat.close_hurt_radius:
                                            opponent_boat.health -= boat.close_damage / 2
                                        elif distance <= boat.near_hurt_radius:
                                            opponent_boat.health -= boat.near_damage / 2
                                        elif distance <= boat.far_hurt_radius:
                                            opponent_boat.health -= boat.far_damage / 2
                                        if opponent_boat.health <= 0: opponent_boat.kill()
                    # Play sound
                    self.mixer.play_sound("effects/break")
                    if "shooting" in boat.abilities:
                        for cannonball2 in boat.cannonballs:  #  Put cannonballs in an orphaned cannonballs group
                            self.cannonballs.append(cannonball2)
                    if boat.team_name == "blue":  # If Blue
                        # Summon Explosion
                        if boat.damaged_island:
                            self.explosions.append(BlueExplosion(boat.position, self.asset_manager))
                        else:
                            self.explosions.append(Explosion(boat.position, self.asset_manager))
                        self.teams.blue.boats.remove(boat)
                    elif boat.team_name == "red":  # If Red
                        # Summon Explosion
                        if boat.damaged_island:
                            self.explosions.append(RedExplosion(boat.position, self.asset_manager))
                        else:
                            self.explosions.append(Explosion(boat.position, self.asset_manager))
                        self.teams.red.boats.remove(boat)
                if boat.won:  # Win
                    if boat.team_name == "blue":
                        print(boat.team_name, "won!")
                        self.running = False
                    elif boat.team_name == "red":
                        print(boat.team_name, "won!")
                        self.running = False

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

        # Draw Boats and Cannonballs and Traps
        for lane in (1, 2, 3):
            for obj in self.traps + self.teams.red.boats + self.teams.blue.boats + self.cannonballs:
                if obj.lane == lane:
                    obj.draw(self.renderer, debug_mode)

        # Draw Explosions
        for explosion in self.explosions:
            explosion.draw(self.renderer, debug_mode)

        # Draw Boat Selector UI
        self.boat_selector_blue.draw_all()
        self.boat_selector_red.draw_all()

        # Draw Upgrade Money Buttons
        self.money_upgrade_blue.draw()
        self.money_upgrade_red.draw()
        # Draw Upgrade Money Labels
        self.money_upgrade_blue_label.draw()
        self.money_upgrade_red_label.draw()

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
        self.renderer.reset_camera()
        if self.running:  # Only draw when In-Game
            self.teams.blue.cursor.draw(self.renderer)
            self.teams.red.cursor.draw(self.renderer)


class PlayerCursor:
    def __init__(self, team: str, position: Vector2, controller, boundary, asset_manager: AssetManager):
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
        self.BOUNDARY: Rect = boundary

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

    def has_hold(self) -> bool:
        return self._prev_click

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
        # Make sure the Cursor is in-bounds
        if self.position.x > self.BOUNDARY.w:
            self.position.x = self.BOUNDARY.w
        elif self.position.x < self.BOUNDARY.x:
            self.position.x = self.BOUNDARY.x
        if self.position.y > self.BOUNDARY.h:
            self.position.y = self.BOUNDARY.h
        elif self.position.y < self.BOUNDARY.y:
            self.position.y = self.BOUNDARY.y

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
    name: str  # Name of the team (red/blue)
    cursor: PlayerCursor  # Colored Cursor
    money: int = 80  # Starting money
    money_cap: int = 1000  # Max money one could have
    money_base_increase: int = 10  # Money $ Per Second ($Money/s)
    money_base_increase_grow_amount: int = 2  # Base money increase amount per upgrade
    money_increase_buy_price: int = 90  # How much it costs to buy upgrade
    money_increase_buy_price_grow_amount: int = 35  # How much more expensive will upgrade cost
    eco_unlock_time: float = 30.0  # How long until the upgrade option unlocks for buying (seconds)
    eco_unlocked: bool = False  # Is eco unlocked?
    boats: list[Boat] = field(default_factory=list)  # List containing all the Boats the team currently has
    island_health: int = 100  # Island health


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
