from __future__ import annotations
import pygame as pg
from pygame import Vector2
from pathlib import Path
from App.settings import load_settings, save_settings
from App.renderer import Renderer
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.camera import DebugCameraController
from App.input import InputManager
from App.ui import SceneManager, UILabel
from App.ui_loader import load_scenes
from World.background import Background

class Game:
    def __init__(self):
        # Load Settings
        self.settings = load_settings()

        # Initialize pygame and Essentials
        pg.init()
        self.debug_mode = True

        self.renderer = Renderer(
            self.settings.main.window_size,
            self.settings.main.render_size,
            self.settings.main.window_title
        )
        self.renderer.reset_camera()
        self.mixer = Mixer()
        self.mixer.load_settings(self.settings)
        self.asset_manager = AssetManager(self.renderer, self.mixer)
        self.asset_manager.load_all()
        self.input_manager = InputManager()

        self.clock = pg.time.Clock()
        self.running = True

        # Set Window Icon
        icon = pg.image.load(Path(__file__).resolve().parent.parent.joinpath("Assets/Images/misc/coin.png"))
        self.renderer.set_icon(icon)

        # Set Input Controllers
        self.debug_controller = DebugCameraController(self.input_manager)
        self.DEBUG_CAMERA_SPEED = 500  # Only for debugging. Used to move camera (Outside)

        # Set Objects
        self.background = Background(self.renderer, self.asset_manager)
        self.scene_library = load_scenes(self.asset_manager)
        self.scene_manager = SceneManager(self.scene_library.scenes, "main_menu")
        self.test_money = 0
        self.test_text = UILabel(pg.Vector2(50, 20), "0", position_mode="center", draw_background=True, text_font=self.asset_manager.get("fonts", "PirataOne"))

        # Set Actions
        self.mixer.play_music("music/Thatched Villagers")

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.WINDOWRESIZED:
                self.settings.main.window_size = self.renderer.window.size
            self.input_manager.process_event(event)

    def handle_ui_interactions(self):
        for e in self.scene_manager.update(self.input_manager, self.mixer, self.renderer.camera.offset):
            # Main Menu
            if e.id == "start_button":
                self.running = False
            elif e.id == "exit_button":
                self.running = False
            elif e.id == "resume_button":
                self.running = False
            elif e.id == "credits_button":
                self.scene_manager.set_scene("credits")
                self.renderer.camera.move(Vector2(-1280, 0))
            elif e.id == "settings_button":
                self.scene_manager.set_scene("main_settings")
                self.renderer.camera.move(Vector2(1280, 0))
            # Credits Page
            elif e.id == "back_button_credits":
                self.scene_manager.set_scene("main_menu")
                self.renderer.camera.move(Vector2(0, 0))
            # Settings Page
            elif e.id == "back_button_settings":
                self.scene_manager.set_scene("main_menu")
                self.renderer.camera.move(Vector2(0, 0))

    def update(self, dt: float):
        # Update Background Elements
        self.background.update(dt)
        # Reset Camera and Update Debug Camera
        self.renderer.reset_camera()
        self.renderer.camera.update(dt, self.debug_controller.get_movement(), self.DEBUG_CAMERA_SPEED)
        # Update UI Scene Functions
        self.handle_ui_interactions()
        self.test_money += 1
        self.test_text.text.content = str(self.test_money)

    def draw(self):
        # Draw the Window Background Color (Clear Screen)
        self.renderer.clear(self.settings.main.window_bg_color)
        # Reset Camera to Main Camera
        self.renderer.reset_camera()
        # Draw Background (Sky and Sea)
        self.background.draw_all()
        # Set Camera to None to Draw UI
        # self.renderer.set_camera(None)
        self.scene_manager.draw(self.renderer, self.asset_manager)
        self.test_text.draw(self.renderer, self.asset_manager)
        # Draw Black Bars
        self.renderer.draw_bars(self.settings.main.window_bg_color)
        # Draw Debug UI
        # Not implemented Yet

    def run(self):
        while self.running:
            # Set delta time
            dt = self.clock.tick(self.settings.main.fps) / 1000.0

            # Main logic
            self.input_manager.begin_frame()
            self.handle_events()
            self.input_manager.mouse_pos_virtual = self.renderer.window_to_virtual(self.input_manager.mouse_pos_window)
            self.update(dt)
            self.draw()

            # Update the screen
            self.renderer.renderer.present()

            # Check if stop run then quit
            if not self.running:
                pg.quit()

        # Save settings and Quit game after loop stops
        save_settings(self.settings)
        pg.quit()
