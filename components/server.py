from .request import Request, REQUEST_SIZE
from .backlog import Backlog
import tkinter as tk
from PIL import Image, ImageTk

SERVER_PADDING = 20
SERVER_H = 2 * SERVER_PADDING + REQUEST_SIZE

IMAGE_SIZE = 35      
SERVER_IMAGE_PATH = 'images/server.png'
DB_IMAGE_PATH = 'images/db.png'
LOAD_BALANCER_PATH = 'images/load_balancer.png'


LOAD_BALANCER_SLAVES_DISTANCE = 200
MAX_SLAVES = 5
SLAVES_DISTANCE = 40


class Server:
    def __init__(
        self,
        app,
        backlog_size: int,
        read_time: int,
        write_time: int,
        x: int | float,
        y: int | float,
        image_paths: list = [SERVER_IMAGE_PATH, DB_IMAGE_PATH]
    ):
        self.app = app
        self.canvas = app.canvas
        self.backlog_size = backlog_size
        self.read_time = read_time
        self.write_time = write_time
        self.x = x
        self.y = y
        self.image_paths = image_paths

        self._init_server()
        self._init_backlog()
        self._init_images()


    def _init_server(self):
        self.server_w = 2 * SERVER_PADDING + self.backlog_size * REQUEST_SIZE + SERVER_PADDING + IMAGE_SIZE
        self.server_h = SERVER_H
        self.total_w = self.server_w + len(self.image_paths) * IMAGE_SIZE
        self.total_h = self.server_h

        self.id = self.canvas.create_rectangle(
            self.x, 
            self.y,
            self.x + self.server_w, 
            self.y + self.server_h,
            fill='gray',
            outline='black'
        )

        self.serving = False

    def _init_backlog(self):
        self.backlog = Backlog(
            canvas=self.canvas,
            x=self.x + SERVER_PADDING,
            y=self.y + SERVER_PADDING,
            size=self.backlog_size
        )

    def _init_images(self):
        images = []
        for path in self.image_paths:
            image = Image.open(path)
            resized_image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
            final_image = ImageTk.PhotoImage(resized_image)
            images.append(final_image)

        self.images = images
        c = 1
        for image in self.images:
            self.canvas.create_image(
                self.x + self.server_w + SERVER_PADDING + (c - 1) * IMAGE_SIZE, 
                self.y + 2 * SERVER_PADDING - 2, 
                image=image,
                anchor=tk.CENTER
            )
            c+=1


    def hit_server(self, request: Request) -> bool:
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        req_x1, req_y1, req_x2, req_y2 =  self.canvas.coords(request.id)
        
        return (
            req_x1 >= x1 and req_x2 <= x2 and
            req_y1 >= y1 and req_y2 <= y2
        )


    def accept_request(self, request: Request) -> bool:
        return self.backlog.accept_request(request)


    def serve_requests(self):
        def get_serving_time(request_type: str) -> int:
            if request_type == 'r':
                return self.read_time
            elif request_type == 'w':
                return self.write_time
            return 0

        if not self.serving:
            if not self.backlog.is_empty():
                self.serving = True
                top_most_req = self.backlog.pop_request()

                if top_most_req:
                    top_most_req.move_to_position(self.x, self.y)

                    serving_time = get_serving_time(top_most_req.request_type)

                    def complete_request():
                        self.response(top_most_req)
                        self.serving = False
                        self.serve_requests()

                    self.app.root.after(serving_time * 1000, complete_request)
            else:
                self.app.root.after(500, self.serve_requests)


    def response(self, request: Request):
        if request.move(50, 500):
            self.app.root.after(30, lambda: self.response(request))
        else:
            self.app.panel.served_queue.add_request(request)
            

class LoadBalancer(Server):
    def __init__(
        self,
        app,
        backlog_size: int,
        read_time: int,
        write_time: int,
        x: int | float,
        y: int | float,
        image_paths: list = [SERVER_IMAGE_PATH, DB_IMAGE_PATH]
    ):
        super().__init__(app, backlog_size, read_time, write_time, x, y, image_paths)
        self.slaves = []

    def serve_requests(self):
        def process_request(request):
            request.move_to_position(self.x, self.y)

            serving_time = 1000

            def complete_request():
                if request.target == 'client':
                    self.response(request)
                elif request.target == 'server':
                    self.slaves.append(self.slaves.pop(0))
                    slave = self.slaves[0]
                    self.forward_request(request, slave)

                self.serving = False
                self.serve_requests()

            self.app.root.after(serving_time, complete_request)

        if not self.serving:
            if not self.backlog.is_empty():
                self.serving = True

                top_most_req = self.backlog.pop_request()

                if top_most_req:
                    process_request(top_most_req)
            else:
                self.app.root.after(500, self.serve_requests)


    def forward_request(self, request: Request, slave):
        x = slave.x
        y = slave.y
        if request.move(x, y):
            self.app.root.after(30, lambda: self.forward_request(request, slave))
        else:
            if slave.hit_server(request):
                if not slave.accept_request(request):
                    self.app.panel.blocked_queue.add_request(request)


    def serve_slave_response(self):
        if not self.serving:
            if not self.backlog.is_empty():
                self.serving = True

                top_most_req = self.backlog.pop_request()
                top_most_req

                if top_most_req:
                    print('Move top most')
                    top_most_req.move_to_position(self.x, self.y)

                    serving_time = 1000
                    def complete_request():
                        self.response(top_most_req)
                        self.serving = False
                        self.serve_slave_response()

                    self.app.root.after(serving_time, complete_request)
            else:
                self.app.root.after(30, self.serve_slave_response())


class Slave(Server):
    def __init__(
        self,
        app,
        backlog_size: int,
        read_time: int,
        write_time: int,
        x: int | float,
        y: int | float,
        load_balancer: LoadBalancer,
        image_paths: list = [LOAD_BALANCER_PATH],
    ):
        self.load_balancer = load_balancer
        super().__init__(app, backlog_size, read_time, write_time, x, y, image_paths)


    def serve_requests(self):
        def get_serving_time(request_type: str) -> int:
            if request_type == 'r':
                return self.read_time
            elif request_type == 'w':
                return self.write_time
            return 0

        def process_request(request):
            request.move_to_position(self.x, self.y)
            request.target = 'client'

            serving_time = get_serving_time(request.request_type)
            print(f"Serving request {request.request_type} for {serving_time} seconds")

            def complete_request():
                self.response(request)
                self.serving = False
                self.serve_requests()

            self.app.root.after(serving_time * 1000, complete_request)

        if not self.serving and not self.backlog.is_empty():
            self.serving = True

            top_most_req = self.backlog.pop_request()

            if top_most_req:
                process_request(top_most_req)
        else:
            self.app.root.after(500, self.serve_requests)



    def response(self, request: Request):
        x = self.load_balancer.x
        y = self.load_balancer.y

        if request.move(x, y):
            self.app.root.after(30, lambda: self.response(request))
        else:
            if self.load_balancer.hit_server(request):
                if not self.load_balancer.accept_request(request):
                    self.app.panel.blocked_queue.add_request(request)
