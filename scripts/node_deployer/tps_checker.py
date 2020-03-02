#!/usr/bin/python3

import json
from datetime import datetime
from websocket import create_connection
import threading

login_req = '{"method": "call", "params": [1, "login", ["", ""]], "id": 0}';
database_req = '{"method": "call", "params": [1, "database", []], "id": 0}'
subscribe_callback_req = '{"method": "set_subscribe_callback", "params": [0, false], "id": 0}'
subscribe_dgpo_req = '{"method": "get_objects", "params": [["2.1.0"]], "id": 0}'
tx_count_req = '{{"method": "get_block_tx_number", "params": [{block_id}], "id": 0}}'

class tps_checker:
    def __init__(self, addr, sent_tx_number):
        url = "ws://{}:8090".format(addr)
        self.tps = 0
        self.collected_tx_number = 0
        self.sent_tx_number = sent_tx_number
        self.start_time = ""
        self.end_time = ""
        self.ws = create_connection(url);
        self.login_api()
        self.collect_tps()
        
    def login_api(self):
        self.ws.send(login_req)
        self.ws.recv()
        self.ws.send(database_req)
        self.ws.recv()
        self.ws.send(subscribe_callback_req)
        self.ws.recv()
        self.ws.send(subscribe_dgpo_req)
        self.ws.recv()

    def collect_tps(self):
        responce = ""
        while self.collected_tx_number != self.sent_tx_number:
            response = json.loads(self.ws.recv())
            block_id = response['params'][1][0][0]['head_block_id']
            block_num = response['params'][1][0][0]['head_block_number']
            self.ws.send(tx_count_req.format(block_id=block_id))
            response_tx = json.loads(self.ws.recv())
            self.collected_tx_number =  self.collected_tx_number + int(response_tx['result'])

            if self.collected_tx_number != 0 and self.start_time == "":
                self.start_time = response['params'][1][0][0]['time']

        self.end_time = response['params'][1][0][0]['time']
        start = datetime.strptime(self.start_time, '%Y-%m-%dT%H:%M:%S')
        end = datetime.strptime(self.end_time, '%Y-%m-%dT%H:%M:%S')
        self.tps = self.collected_tx_number / (start - end).seconds

    def get_tps(self):
        return self.tps

    def run_check(self):
        self.t = threading.Thread(target=self.collect_tps)
        self.t.start()

    def wait_check(self):
        self.t.join()

#def test():
#    tc = tps_checker("172.17.0.2", 10)
#    tc.wait_check()
#    print("Tps : ", tc.get_tps())
#
#test()
