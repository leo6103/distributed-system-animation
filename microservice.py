import tkinter as tk
from components.request import Request, REQUEST_SIZE, DEFAULT_SPEED
from components.server import (
    Server,
    LoadBalancer,
    Slave,
    SERVER_H, 
    SERVER_IMAGE_PATH, 
    DB_IMAGE_PATH,
    LOAD_BALANCER_PATH,
    LOAD_BALANCER_SLAVES_DISTANCE,
    MAX_SLAVES,
    SLAVES_DISTANCE
)
from components.panel import Panel, Queue, PANEL_H
from utils.config import load_config, get_request_config, get_server_config, get_load_balancer_config

WINDOW_H = 1080
WINDOW_W = 1920


# Position for simulation
REQUEST_X = 50
REQUEST_Y = 500

MASTER_X = 500
MASTER_Y = (WINDOW_H - SERVER_H - PANEL_H) / 2


SLAVE_X = MASTER_X



class App:
    def __init__(self, root: tk.Tk, config: dict):
        self.root = root
        self.root.title('Ticket Selling Microservice')
        self.root.geometry(f'{WINDOW_W}x{WINDOW_H}')

        self.config = config
        self.requests_config = get_request_config(config)
        self.load_balancer_config = get_load_balancer_config(config)
        
        self.requests = []
        self.slaves = []

        self.canvas = tk.Canvas(self.root, width=WINDOW_W, height=WINDOW_H, bg='white')
        self.canvas.pack()

        self._init_panel()
        self._init_load_balancer()
        self._init_slaves()
        

        self._start_simulation()


    def _init_panel(self):
        self.panel = Panel(self.canvas, w=WINDOW_W, h=PANEL_H)

    def _init_load_balancer(self):
        self.load_balancer = LoadBalancer(
            self,
            backlog_size=self.load_balancer_config.get('backlog'),
            read_time=self.load_balancer_config.get('read_time'),
            write_time=self.load_balancer_config.get('write_time'),
            x=MASTER_X,
            y=MASTER_Y,
            image_paths=[LOAD_BALANCER_PATH]
        )
        # self.load_balancer.serve_slave_response()
        self.load_balancer.serve_requests()

    def _init_slaves(self):
        slaves_x = self.load_balancer.x + self.load_balancer.total_w + LOAD_BALANCER_SLAVES_DISTANCE
        top_most_y = self.load_balancer.y - (MAX_SLAVES // 2) * (self.load_balancer.total_h + SLAVES_DISTANCE)

        slave_y = top_most_y
        for i in range(5):
            slave = Slave(
                self,
                backlog_size=5,
                read_time=5,
                write_time=5,
                x=slaves_x,
                y=slave_y,
                load_balancer=self.load_balancer,
                image_paths=[SERVER_IMAGE_PATH, DB_IMAGE_PATH]
            )
            slave.serve_requests()
            slave_y += SLAVES_DISTANCE + slave.total_h
            self.slaves.append(slave)
            self.load_balancer.slaves.append(slave)

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

        self._send_to_load_balancer(request)

    def _send_to_load_balancer(self, request: Request):
        if request.move(self.load_balancer.x, self.load_balancer.y):
            self.root.after(30, lambda: self._send_to_load_balancer(request))
        else:
            if self.load_balancer.hit_server(request):
                if not self.load_balancer.accept_request(request):
                    self.panel.blocked_queue.add_request(request)
                else:
                    self.load_balancer.serve_requests()

if __name__ == '__main__':
    root = tk.Tk()
    config = load_config('config.json')
    app = App(root, config)
    root.mainloop()