import pygame as pg
from pygame import Vector2
from App.input import InputManager
from App.debug import debug_print


debug_mode = False

class Camera2D:
    def __init__(self, start_position=None, smoothness=5):
        # Camera position is top-left
        self.offset = Vector2(start_position) if start_position is not None else Vector2(0, 0)
        # Where to go. Used for Camera Smoothing
        self.target_offset = Vector2(start_position) if start_position is not None else Vector2(0, 0)
        self.smoothing = True  # Camera Smoothing. Good for move() teleport type movements
        self.smoothness = smoothness

    def update(self, dt: float):
        if self.smoothing:
            self.offset += (self.target_offset - self.offset) * self.smoothness * dt
        debug_print(self.offset, debug_mode)

    def debug_update(self, dt: float, debug_movement=None, debug_camera_speed=500):
        if debug_movement is not None:
            self.slide(*debug_movement*debug_camera_speed*dt)

    def move(self, pos: Vector2, smoothness=5):
        self.smoothness = smoothness
        if self.smoothing:
            self.target_offset = pos
        else:
            self.offset = pos
            self.target_offset = pos  # Set here, so when re-enabling smoothing, it doesn't tweak out

    def slide(self, x, y):
        # Move x y amount from current position
        self.move(self.target_offset + Vector2(x, y))
