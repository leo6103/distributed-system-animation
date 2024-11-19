import tkinter as tk
from components.request import Request, REQUEST_SIZE, DEFAULT_SPEED
from components.server import Server, SERVER_H
from components.panel import PANEL_H
from PIL import Image, ImageTk


WINDOW_H = 1080
WINDOW_W = 1920


# Position for simulation
REQUEST_X = 50
REQUEST_Y = 500

MASTER_X = 500
MASTER_Y = (WINDOW_H - SERVER_H - PANEL_H) / 2


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Ticket Selling')
        self.root.geometry(f'{WINDOW_W}x{WINDOW_H}')

        self.canvas = tk.Canvas(self.root, width=WINDOW_W, height=WINDOW_H, bg='white')
        self.canvas.pack()

        self._init_panel()
        self._init_server()

    def _init_panel(self):
        pass

    def _init_server(self):
        self.server = Server(self, backlog_size=5, x=MASTER_X, y=MASTER_Y)

    def _init_requests(self):
        pass


    def test_simulate(self):
        self.server = Server(self, 5, 500, 500)
        request = Request(self, 50, 50, 35, 'blue')
        self.send_to_server(request, 500, 500)


    def send_to_server(self, request: Request, x: int | float, y: int | float) -> bool:
        if request.move(x, y):
            request.canvas.after(30, lambda: self.send_to_server(request, x, y))
        else:
            print('reached')


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
