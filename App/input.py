import pygame as pg

class InputManager:
    def __init__(self):
        self.keys_down = set()
        self.keys_pressed = set()
        self.keys_released = set()

        self.mouse_down = set()
        self.mouse_pressed = set()
        self.mouse_released = set()

        self.mouse_pos_window = (0, 0)
        self.mouse_pos_virtual = (0, 0)

    def begin_frame(self):
        # Clear states
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_pressed.clear()
        self.mouse_released.clear()
        # Update Mouse Position
        self.mouse_pos_window = pg.mouse.get_pos()

    def process_event(self, e):
        # Keyboard Events
        if e.type == pg.KEYDOWN:
            if e.key not in self.keys_down:
                self.keys_pressed.add(e.key)
            self.keys_down.add(e.key)
        elif e.type == pg.KEYUP:
            self.keys_down.discard(e.key)
            self.keys_released.add(e.key)
        # Mouse Events # 1=LeftClick 2=MiddleClick 3=RightClick 4=ScrollUp 5=ScrollDown
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button not in self.mouse_down:
                self.mouse_pressed.add(e.button)
            self.mouse_down.add(e.button)
        elif e.type == pg.MOUSEBUTTONUP:
            self.mouse_down.discard(e.button)
            self.mouse_released.add(e.button)

    def is_key_down(self, key):
        return key in self.keys_down

    def was_key_pressed(self, key):
        return key in self.keys_pressed

    def was_key_released(self, key):
        return key in self.keys_released

    def is_mouse_down(self, key):
        return key in self.mouse_down

    def was_mouse_pressed(self, key):
        return key in self.mouse_pressed

    def was_mouse_released(self, key):
        return key in self.mouse_released
