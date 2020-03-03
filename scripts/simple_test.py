from time import sleep

from node_deployer.deployer import deployer
from node_deployer.utilization_checker import utillization_checker
from node_deployer.tps_checker import tps_checker
from node_sender.sender import Sender

class simple_test:
    def __init__(self, node_count, echo_bin, image, tx_count):
        self.tx_count = tx_count
        d = deployer(node_count=node_count, echo_bin=echo_bin, image=image)
        sleep(60)
        self.uc = utillization_checker(d.get_addresses(), d.get_node_names())
        self.s = Sender("ws://172.17.0.2:8090/ws")
        self.s.import_balance_to_nathan()
        sleep(20)

    def run_test(self):
        self.uc.run_check()
        tc = tps_checker("172.17.0.2", self.tx_count)
        tc.run_check()
        self.s.transfer(self.tx_count)
        tc.wait_check()
        self.uc.stop_check()

def test():
    test = simple_test(10, "/home/vadim/PixelPlex/echo/build/bin/echo_node", "ubuntu_delay", 50000)
    test.run_test()

test()