import tkinter as tk
from .request import Request, REQUEST_SIZE

PANEL_H = 80

class Queue:
    def __init__(
        self,
        canvas: tk.Canvas,
        x: int | float,
        y: int | float,
        label: str,
        size: int
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.label = label
        self.size = size
        self.queue = []

        self.canvas.create_rectangle(
            self.x,
            self.y,
            self.x + REQUEST_SIZE * size,
            self.y + REQUEST_SIZE,
            fill='white',
            outline='black'
        )
        # TODO : Add new queue for saving served time
        self.canvas.create_text(
            self.x + REQUEST_SIZE * size / 2,
            self.y - 10, text=self.label
        )

    def add_request(self, request: Request):
        if len(self.queue) < self.size:
            slot_x = self.x + len(self.queue) * REQUEST_SIZE
            slot_y = self.y
            request.move_to_position(slot_x, slot_y)
            self.queue.append(request)



class Panel:
    def __init__(
        self,
        canvas: tk.Canvas,
        w: int | float,
        h: int | float,
        bg='gray'
    ):
        self.canvas = canvas
        self.w = w
        self.h = h
        self.bg = bg

        self.id = self.canvas.create_rectangle(
            0,
            0,
            self.w,
            self.h,
            fill=self.bg,
            outline='black'
        )

        self._init_queues()
        self._init_timer()
        self._init_logger()


    def _init_queues(self):
        size = 30
        self.served_queue = Queue(self.canvas, x=100, y=20, label='Served', size=size)
        self.blocked_queue = Queue(self.canvas, x=100 + REQUEST_SIZE * size + 20, y=20, label='Blocked',size=10)

    def _init_timer(self):
        pass

    def _init_logger(self):
        pass