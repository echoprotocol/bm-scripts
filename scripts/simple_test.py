from time import sleep

from node_deployer.deployer import deployer
from node_deployer.utilization_checker import utillization_checker
from node_deployer.tps_checker import tps_checker
from node_sender.sender import Sender

class simple_test:
    def __init__(self, node_count, echo_bin, image, tx_count):
        self.tx_count = tx_count
        self.d = deployer(node_count=node_count, echo_bin=echo_bin, image=image)
        self.d.wait_nodes()
        self.s = Sender("ws://172.17.0.2:8090/ws")
        self.s.import_balance_to_nathan()

    def run_test(self):
        # self.s.create_contract(with_response = True)
        uc = utillization_checker(self.d.get_addresses(), self.d.get_node_names())
        uc.run_check()
        tc = tps_checker("172.17.0.2", self.tx_count)
        tc.run_check()
        self.s.create_contract(transaction_count = self.tx_count)
        tc.wait_check()
        uc.stop_check()

def test():
    test = simple_test(10, "/home/vadim/PixelPlex/echo/build/bin/echo_node", "ubuntu_delay", 1000)
    test.run_test()

test()
