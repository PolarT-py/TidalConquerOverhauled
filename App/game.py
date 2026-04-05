from __future__ import annotations
import pygame as pg
from pathlib import Path
from App.settings import load_settings, save_settings
from App.renderer import Renderer
from App.asset_manager import AssetManager
from App.mixer import Mixer
from App.camera import DebugCameraController
from App.input import InputManager
from App.ui import SceneManager
from App.ui_loader import load_scenes
from App.debug import debug_print
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

        # Set Actions
        self.mixer.play_sound("effects/click1")  # Test opening sound
        self.mixer.play_music("music/Thatched Villagers")
        # self.renderer.camera.slide(500, 100)  # Test Camera Movement

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.WINDOWRESIZED:
                self.settings.main.window_size = self.renderer.window.size
            self.input_manager.process_event(event)

    def update(self, dt: float):
        # Update Background Elements
        self.background.update(dt)
        # Reset Camera and Update Debug Camera
        self.renderer.reset_camera()
        self.renderer.camera.update(dt, self.debug_controller.get_movement(), self.DEBUG_CAMERA_SPEED)
        # Update Test Scene
        self.scene_manager.current_scene.update_all(self.input_manager)

    def draw(self):
        # Draw the Window Background Color (Clear Screen)
        self.renderer.clear(self.settings.main.window_bg_color)
        # Reset Camera to Main Camera
        self.renderer.reset_camera()
        # Draw Background (Sky and Sea)
        self.background.draw_all()
        # Set Camera to None to Draw UI
        self.renderer.set_camera(None)
        self.scene_manager.current_scene.draw_all(self.renderer, self.asset_manager)
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

        # Save settings and Quit game after loop stops
        save_settings(self.settings)
        pg.quit()
