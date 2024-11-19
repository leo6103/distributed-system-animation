import tkinter as tk
from components.request import Request, REQUEST_SIZE, DEFAULT_SPEED
from components.server import Server, SERVER_H, SERVER_IMAGE_PATH, DB_IMAGE_PATH
from components.panel import Panel, Queue, PANEL_H
from utils.config import load_config, get_request_config, get_server_config

WINDOW_H = 1080
WINDOW_W = 1920


# Position for simulation
REQUEST_X = 50
REQUEST_Y = 500

MASTER_X = 500
MASTER_Y = (WINDOW_H - SERVER_H - PANEL_H) / 2


class App:
    def __init__(self, root: tk.Tk, config: dict):
        self.root = root
        self.root.title('Ticket Selling Monolithic')
        self.root.geometry(f'{WINDOW_W}x{WINDOW_H}')

        self.config = config
        self.requests_config = get_request_config(config)
        self.server_config = get_server_config(config)
        self.requests = []

        self.canvas = tk.Canvas(self.root, width=WINDOW_W, height=WINDOW_H, bg='white')
        self.canvas.pack()

        self._init_panel()
        self._init_server()
        self._start_simulation()

    def _init_panel(self):
        self.panel = Panel(self.canvas, w=WINDOW_W, h=PANEL_H)

    def _init_server(self):
        self.server = Server(
            self, 
            backlog_size=self.server_config.get('backlog'),
            read_time=self.server_config.get('read_time'),
            write_time=self.server_config.get('write_time'),
            x=MASTER_X, 
            y=MASTER_Y,
            image_paths=[SERVER_IMAGE_PATH, DB_IMAGE_PATH]
        )

    def _simulate_requests(self):
        pass

    def _start_simulation(self):
        for request_config in self.requests_config:
            arrival_time = request_config.get('arrival_time', 0) * 1000
            self.root.after(arrival_time, lambda req_config = request_config: self._create_and_send_request(req_config))

    def _create_and_send_request(self, request_config: dict):
        request_num = request_config.get('id')
        request = Request(
            self,
            x=REQUEST_X,
            y=REQUEST_Y,
            request_type=request_config.get('request_type')
        )
        request.add_label(str(request_num))
        self.requests.append(request)

        self._send_to_server(request)

    def _send_to_server(self, request: Request):
        if request.move(self.server.x, self.server.y):
            self.root.after(30, lambda: self._send_to_server(request))
        else:
            if self.server.hit_server(request):
                if not self.server.accept_request(request):
                    self.panel.blocked_queue.add_request(request)
                else:
                    self.server.serve_requests()


if __name__ == '__main__':
    root = tk.Tk()
    config = load_config('config.json')
    app = App(root, config)
    root.mainloop()
