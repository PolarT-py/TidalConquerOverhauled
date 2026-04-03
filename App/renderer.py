class Renderer:
    def __init__(self, target_surface):
        self.target = target_surface

    def clear(self, color):
        self.target.fill(color)

    def draw(self, texture, pos):
        self.target.blit(texture, pos)
