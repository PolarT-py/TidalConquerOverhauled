import pygame
from App.settings import load_settings, save_settings
from App.renderer import Renderer

class Game:
    def __init__(self):
        # Load Settings
        self.settings = load_settings()

        # Initialize pygame and Essentials
        pygame.init()

        self.window = pygame.display.set_mode(self.settings.main.window_size, pygame.RESIZABLE)
        pygame.display.set_caption(self.settings.main.window_title)

        self.render_size = (1280, 720)
        self.screen = pygame.Surface(self.render_size)
        self.renderer = Renderer(self.screen)
        self.test_texture = pygame.image\
    .load("/home/polar/PycharmProjects/TidalConquerOverhauled/Assets/Images/boats/boat1.png")\
    .convert_alpha()

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float):
        # nothing yet
        pass

    def render_to_window(self):
        # Draw the Window Background Color
        self.window.fill(self.settings.main.window_bg_color)
        # Calculate Scaling and Positions
        window_width, window_height = self.window.get_size()
        render_width, render_height = self.render_size

        scale = min(window_width / render_width, window_height / render_height)
        scaled_width = int(render_width * scale)
        scaled_height = int(render_height * scale)
        scaled_surface = pygame.transform.scale(self.screen, (scaled_width, scaled_height))

        x = (window_width - scaled_width) // 2
        y = (window_height - scaled_height) // 2
        # Draw the Screen onto the Window
        self.window.blit(scaled_surface, (x, y))

    def draw(self):
        # Draw the Screen Background Color
        self.screen.fill((0, 0, 0))
        # Draw Test Object
        self.renderer.draw(self.test_texture, (100, 100)) # Test draw
        # Draw the Screen onto the Window
        self.render_to_window()

    def run(self):
        while self.running:
            # Set delta time
            dt = self.clock.tick(self.settings.main.fps) / 1000.0

            # Main logic
            self.handle_events()
            self.update(dt)
            self.draw()

            # Update the screen
            pygame.display.flip()

        # Save settings and Quit game after loop stops
        save_settings(self.settings)
        pygame.quit()
