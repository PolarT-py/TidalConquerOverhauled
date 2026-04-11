from pygame import Vector2, Rect
from App.clock import Timer
from App.renderer import Texture2D


class Animation:
    def __init__(self, position: Vector2, wait_time=0.0):
        self.fps = 12  # Set FPS
        self.flip_timer = Timer(1/self.fps, False, True)  # Set Animation Flip Timer
        self.frames: list[Texture2D] = []  # Animation Frames
        self.frame = 0  # Start on 1st Frame
        self.position: Vector2 = position  # Set Position
        self.finished = False  # If finished or not
        self.wait_timer = Timer(wait_time, True)  # How much to wait before starting
        self.can_animation = True if wait_time == 0 else False  # Wait time before being visible

    def start(self):
        self.can_animation = True
        self.flip_timer.reset()

    def update(self, dt: float):
        if self.wait_timer.update(dt):
            self.start()
        if self.can_animation:
            # If it's time to switch to the next frame
            if self.flip_timer.update(dt):
                self.frame += 1  # Increment frame by 1
                if self.frame >= len(self.frames):  # If there are no more frames
                    self.finished = True

    def draw(self, renderer, debug_mode=False):
        if not self.finished:  # Check if animation is done
            # Draw the frame if it can animate
            if self.can_animation:
                frame: Texture2D = self.frames[self.frame]
                renderer.draw_texture(
                    frame,
                    pos=self.position,
                    position_mode="center"
                )
            if debug_mode:
                # Draw Debug Hitbox
                color = (255, 165, 0)
                frame_w, frame_h = self.frames[self.frame].size
                rect = Rect(0, 0, frame_w, frame_h)
                rect.center = (self.position.x, self.position.y)
                renderer.draw_rect(rect, color=(*color, 100))
