import pygame
fps = 60

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption("Tidal Conquer: Overhauled")

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float):
        # nothing yet
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))

    def run(self):
        while self.running:
            dt = self.clock.tick(fps) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

            pygame.display.flip()

        pygame.quit()
