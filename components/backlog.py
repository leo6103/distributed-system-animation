from .request import Request, REQUEST_SIZE
import tkinter as tk

SERVER_H = 100
SLAVE_DISTANCE = 80


class Backlog:
    def __init__(
        self, 
        canvas: tk.Canvas,
        x: int | float,
        y: int | float,
        size: int = 5
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.queue = []

        self.id = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + REQUEST_SIZE * self.size, self.y + REQUEST_SIZE,
            fill="white",
            outline="black"
        )


    def accept_request(self, request: Request) -> bool:
        if len(self.queue) >= self.size:
            return False
        
        slot_x = self.x + len(self.queue) * REQUEST_SIZE
        slot_y = self.y
        self.queue.append(request)
        request.move_to_position(slot_x, slot_y)

        return True


    def pop_request(self) -> Request:
        def rearrange_queue():
            for index, request in enumerate(self.queue):
                slot_x = self.x + index * REQUEST_SIZE 
                slot_y = self.y
                request.move_to_position(slot_x, slot_y)

        if self.queue:
            removed_request = self.queue.pop(0)
            rearrange_queue()

            return removed_request
