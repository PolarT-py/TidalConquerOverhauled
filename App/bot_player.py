from typing import TYPE_CHECKING
from dataclasses import dataclass
from App.clock import Timer
from random import randint, choice
from App.debug import debug_print
if TYPE_CHECKING:
    from App.in_game import InGame


class BotPlayer:
    def __init__(self, game_obj):
        self.game_obj: InGame = game_obj  # All the game's data
        self.game = GameDatabase(self.game_obj)  # Clean database of the Game's Data
        self.behavior = "chill"  # What it'll do depending on data (chill/attack/defend/emergency)
        self.tick_timer: Timer = Timer(0.5, start=True, repeat=True)  # How often it updates
        self.secondary_lane = None  # Focus Lanes
        self.focus_lane = None  # Focus Lanes
        self.sorted_lanes = []  # Lanes sorted by strength differences

    def has_attack_opportunity(self):
        # Check for open lane and if the enemy is poor
        for lane in self.game.lanes:
            if lane.enemy_amount == 0:
                if self.game.enemy_money < 60:
                    return True

        # Weak lane compared to others
        enemy_strengths = [lane.enemy_strength for lane in self.game.lanes]
        weakest = min(enemy_strengths)
        strongest = max(enemy_strengths)

        if strongest - weakest >= 4 and self.game.money >= 50:
            return True

        return False

    def choose_behavior(self):
        # Sort the lanes by threat level
        self.sorted_lanes = list(enumerate(self.game.lanes, start=1))
        self.sorted_lanes.sort(key=lambda item: item[1].threat, reverse=True)

        # Save lanes to focus on
        self.focus_lane = self.sorted_lanes[0][0]
        self.secondary_lane = self.sorted_lanes[1][0]

        highest = self.sorted_lanes[0][1]
        second = self.sorted_lanes[1][1]

        # Emergency = A Lane has a large threat or two lanes both are bad
        if highest.threat >= 8 or (highest.threat >= 6 and second.threat >= 6):
            self.behavior = "emergency"
        # Defend = A Lane needs attention
        elif highest.threat >= 4 or highest.strength_diff >= 3 or second.strength_diff >= 3:
            self.behavior = "defend"
        # Attack = A Lane has few enemies and it's safe overall
        elif self.has_attack_opportunity() and highest.threat <= 2 and second.threat <= 2 and self.game.money >= 50:
            self.behavior = "attack"
        # Chill = Nothing is going on. Buy Eco or start an attack
        else:
            self.behavior = "chill"

    def place(self, lane, minimum_reserve=None, emergency=False):  # Places currently selected boat
        if self.game_obj.teams.red.cursor.status != "normal":
            return
        selected_item = self.game_obj.teams.red.cursor.selected_item
        cost = self.game_obj.boat_registry[selected_item].cost
        remaining_money = self.game.money - cost
        # Can't afford the boat at all
        if self.game.money < cost:
            return
        # If it's an emergency, ignore all reserves
        if emergency:
            self.game_obj.add_boat("red", selected_item, lane)
            return
        # Use reserve given, else use normal reserve
        if minimum_reserve is None:
            minimum_reserve = self.game.MINIMUM_RESERVE

        if remaining_money >= minimum_reserve:
            self.game_obj.add_boat("red", selected_item, lane)

    def update_boat_selector_icon(self):
        self.game_obj.boat_selector_red.selected_key = self.game_obj.teams.red.cursor.selected_item

    def do_behavior(self, dt):
        if self.behavior == "emergency":
            self.do_emergency()
        elif self.behavior == "defend":
            self.do_defend()
        elif self.behavior == "attack":
            self.do_attack()
        else:  # Bot Chilling
            self.do_chill(dt)

    def do_emergency(self):
        cursor = self.game_obj.teams.red.cursor
        if self.game.money >= 50:
            selected_item = "TankBoat"
        else:
            selected_item = "SpeedBoat"
        cursor.selected_item = selected_item
        self.place(self.focus_lane, emergency=True)

    def do_defend(self):
        cursor = self.game_obj.teams.red.cursor
        selected_item = None
        highest = self.sorted_lanes[0][1]  # Most dangerous lane
        if self.game.money >= 120:
            items = [
                "ExplosiveBoat",
                "SpeedBoat",
                "SpeedBoat",
                "CannonBoat",
                "CannonBoat",
                "TankBoat",
                "TankBoat",
                "TankBoat",
                "TankBoat",
                "TankBoat",
            ]
            if highest.enemy_amount > 5:  # If there are a lots of enemies, place Explosive Boats more often
                items += ["ExplosiveBoat"] * 2
            selected_item = choice(items)
        elif self.game.money >= 50:
            selected_item = choice([
                "SpeedBoat",
                "TankBoat",
                "TankBoat",
                "TankBoat",
            ])
        elif self.game.money >= 20:
            selected_item = "SpeedBoat"
        if selected_item is not None:
            cursor.selected_item = selected_item
            self.place(self.focus_lane)

    def do_attack(self):
        cursor = self.game_obj.teams.red.cursor
        selected_item = None
        # List of possible boats based on how much money you've got
        options = []
        if self.game.money >= 120:
            options += ["CannonBoat"] * 2 + ["TankBoat"] * 3 + ["SpeedBoat"] * 2
        elif self.game.money >= 80:
            options += ["CannonBoat"] * 1 + ["TankBoat"] * 2 + ["SpeedBoat"] * 2
        elif self.game.money >= 50:
            options += ["TankBoat"] * 3 + ["SpeedBoat"] * 2
        elif self.game.money >= 20:
            options += ["SpeedBoat"]
        if options:
            # Pick randomly from options
            selected_item = choice(options)
            # Choose a random lane to attack
            lane = randint(1, 3)
            cursor.selected_item = selected_item
            self.place(lane, minimum_reserve=self.game.MINIMUM_ATTACK_RESERVE)

    def do_chill(self, dt):
        # Start a fight randomly
        start_a_fight = randint(1, 10)
        if start_a_fight == 1:
            self.game_obj.teams.red.cursor.selected_item = "SpeedBoat"
            lane = randint(1, 3)
            self.place(lane, minimum_reserve=self.game.MINIMUM_CHILL_RESERVE)
        # Buy Eco if possible
        if self.game.money >= self.game_obj.teams.red.money_increase_buy_price:
            self.game_obj.bot_buy_eco(dt)

    def update(self, dt: float, debug_mode=False):
        if self.tick_timer.update(dt):  # New update tick
            # Update Game Database
            self.game.update()

            # Set Behavior
            self.choose_behavior()

            # Do Behavior
            self.do_behavior(dt)
            self.update_boat_selector_icon()

            # Print Debug
            debug_print(f"-- New Tick", debug_mode)
            debug_print(f"Behavior: {self.behavior.capitalize()}", debug_mode)
            debug_print(f"Money: {self.game_obj.teams.red.money}", debug_mode)
            debug_print(
                f"Lane 1 Threat: {self.game.lanes[0].threat} - Strength Diff: {self.game.lanes[0].strength_diff}",
                debug_mode)
            debug_print(
                f"Lane 2 Threat: {self.game.lanes[1].threat} - Strength Diff: {self.game.lanes[1].strength_diff}",
                debug_mode)
            debug_print(
                f"Lane 3 Threat: {self.game.lanes[2].threat} - Strength Diff: {self.game.lanes[2].strength_diff}",
                debug_mode)


@dataclass
class LaneData:  # Stores Data on different things on the lane
    threat: float = 0.0  # Calculated using enemy_strength and friendly_strength and closest_enemy 0.0-1.0
    enemy_amount: int = 0  # The number of enemies in the lane
    friendly_amount: int = 0  # The number of friendlies in the lane
    enemy_strength: float = 0.0  # Total strength of every enemy on this lane, amount varies on boat types
    friendly_strength: float = 0.0  # Total strength of every friendly on this lane, amount varies also
    strength_diff: float = 0.0  # Difference between Friendly VS. Enemy strength
    closest_enemy_distance: float = 0.0  # Distance of the closest enemy to the island


class GameDatabase:
    def __init__(self, game_obj):
        # Game Object
        self.game_obj: InGame = game_obj
        # Lane Objects
        self.lanes = [LaneData(), LaneData(), LaneData()]
        # CONSTANTS
        self.CRITICAL_DISTANCE = 500  # Distance to the most right screen edge
        self.MINIMUM_RESERVE = 50
        self.MINIMUM_ATTACK_RESERVE = 100
        self.MINIMUM_CHILL_RESERVE = 200
        # Other Game Data
        self.money = self.game_obj.teams.red.money
        self.enemy_money = self.game_obj.teams.blue.money

    def update(self):
        # Update Game Info
        self.money = self.game_obj.teams.red.money
        self.enemy_money = self.game_obj.teams.blue.money
        # Clear Lane Data
        self.lanes = [LaneData(), LaneData(), LaneData()]
        # Get Enemy Boats (Blue)
        for boat in self.game_obj.teams.blue.boats:
            lane = self.lanes[boat.lane-1]  # Get Lane
            # Add basic info
            lane.enemy_amount += 1
            lane.enemy_strength += boat.threat
            # Calculate Distance
            distance = abs(self.game_obj.settings.main.render_size[0] - boat.position.x)
            # Compare Distances to set the new closest distance in Lane
            if lane.closest_enemy_distance == 0.0 or distance < lane.closest_enemy_distance:
                lane.closest_enemy_distance = distance

        # Get Friendly Boats (Red)
        for boat in self.game_obj.teams.red.boats:
            lane = self.lanes[boat.lane-1]  # Get Lane
            # Add basic info
            lane.friendly_amount += 1
            lane.friendly_strength += boat.threat

        # Update Lane Data
        for lane in self.lanes:
            # No enemies in lane, skip (No threats)
            if lane.enemy_amount == 0:
                lane.threat = 0.0
                continue

            # Enemy strength VS. Friendly strength
            lane.strength_diff = lane.enemy_strength - lane.friendly_strength
            strength_ratio = lane.enemy_strength / (lane.friendly_strength + 1)
            # Danger with Distance level
            distance_factor = 1.0 - (lane.closest_enemy_distance / self.CRITICAL_DISTANCE)

            # Calculate lane threat amount
            lane.threat = (strength_ratio * 0.6) + (distance_factor * 0.4)
            # If enemy in Critical distance, boost threat amount
            if lane.closest_enemy_distance < self.CRITICAL_DISTANCE:
                proximity = 1.0 - (lane.closest_enemy_distance / self.CRITICAL_DISTANCE)  # Scale by dist
                lane.threat += proximity * 20.0
