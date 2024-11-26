import tkinter as tk

DEFAULT_SPEED = 400
REQUEST_SIZE = 35


class Request:
    def __init__(
        self, 
        app,
        x: int | float,
        y: int | float,
        request_type: str,
        size: int | float = REQUEST_SIZE,
        color: str = 'blue',
        speed: int | float = DEFAULT_SPEED 
    ):
        self.app = app
        self.canvas = self.app.canvas
        self.x = x
        self.y = y
        self.request_type = request_type
        self.size = size
        self.speed = speed
        self.text = None

        self.id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.size, self.y + self.size,
            fill=color,
            outline='black'
        )
        self.target = 'server'

    def add_label(self, text: str):
        self.text = self.canvas.create_text(
            self.x + self.size // 2,
            self.y + self.size // 2,
            text=text,
            fill='white'
        )

    def move(self,  x: int | float, y: int | float, time_interval=30) -> bool:
        '''Move step by step'''
        step_distance = self.speed * (time_interval / 1000)

        x1, y1, _, _ = self.canvas.coords(self.id)

        distance_x = x - x1
        distance_y = y - y1
        total_distance = (distance_x**2 + distance_y**2) ** 0.5

        if total_distance <= step_distance:
            dx = x - x1
            dy = y - y1
            self.canvas.move(self.id, dx, dy)
            if self.text:
                self.canvas.move(self.text, dx, dy)

            return False

        dx = (distance_x / total_distance) * step_distance
        dy = (distance_y / total_distance) * step_distance

        self.canvas.move(self.id, dx, dy)
        if self.text:
            self.canvas.move(self.text, dx, dy)

        return True

    def move_to_position(self, x: int | float, y: int | float):
        '''Move instantly'''
        self.canvas.coords(
            self.id,
            x, y,
            x + self.size, y + self.size
        )
        if self.text:
            self.canvas.coords(
                self.text,
                x + self.size // 2,
                y + self.size // 2
            )
