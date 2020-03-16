#!/usr/bin/python3

import time
from websocket import create_connection
import json
import threading

login_req = '{"method": "call", "params": [1, "login", ["", ""]], "id": 0}';
database_req = '{"method": "call", "params": [1, "database", []], "id": 0}'
pending_callback = '{"method": "set_pending_transaction_callback", "params": ["0"], "id": 0}'

class propagation_checker:
    def __init__(self, addr, port):
        self.is_interrupted = False
        url = "ws://{}:{}".format(addr, port)
        self.ws = create_connection(url)
        self.login_api()
        self.time = 0.0
        
    def login_api(self):
        self.ws.send(login_req)
        self.ws.recv()
        self.ws.send(database_req)
        self.ws.recv()

    def send_and_wait(self, tx):
        try:
            self.ws.send(pending_callback)
            self.ws.recv()
            while self.is_interrupted == False:
                response = json.loads(self.ws.recv())
                if "params" in response and tx._signatures == response['params'][1][0]['signatures']:
                    self.time = time.time()
                    break
        except:
            pass

    def run_check(self, tx):
        self.t = threading.Thread(target=self.send_and_wait, args=(tx,))
        self.t.start()

    def wait_check(self):
        self.t.join()

    def get_time(self):
        return self.time

    def interrupt_checker(self):
        self.ws.close()
        self.is_interrupted = True
        self.wait_check()
