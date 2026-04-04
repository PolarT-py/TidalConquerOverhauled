from pygame import Vector2

class Camera2D:
    def __init__(self, start_position=None):
        # Camera position is top-left
        self.offset = Vector2(start_position) if start_position is not None else Vector2(0, 0)
        # Where to go. Used for Camera Smoothing
        self.target_offset = Vector2(start_position) if start_position is not None else Vector2(0, 0)
        self.smoothing = True  # Camera Smoothing. Good for move() teleport type movements
        self.smoothness = 0.25  # Silly magic number. KEEP IT LIKE THIS!!!
        self.DEBUG_CAMERA_SPEED = 500  # Only for debugging. Used to move camera (Outside)

    def update(self, dt: float):
        if self.smoothing:
            self.offset += (self.target_offset - self.offset) / self.smoothness * dt

    def move(self, pos: Vector2):
        if self.smoothing:
            self.target_offset = pos
        else:
            self.offset = pos
            self.target_offset = pos  # Set here, so when re-enabling smoothing, it doesn't tweak out

    def slide(self, x, y):
        # Move x y amount from current position
        self.move(self.target_offset + Vector2(x, y))
