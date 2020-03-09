from time import sleep

from .node_deployer.deployer import deployer
from .node_deployer.utilization_checker import utillization_checker
from .node_deployer.tps_checker import tps_checker
from .node_sender.sender import Sender
from .utils.utils import tx_ratio

class database_size_test:
    def __init__(self, node_count, echo_bin, image, tx_count = 1000, cycles = 1):
        self.tx_count = tx_count
        self.cycles = cycles
        self.d = deployer(node_count=node_count, echo_bin=echo_bin, image=image)
        self.d.wait_nodes()
        self.s = Sender(self.d.get_addresses()[0])
        self.s.import_balance_to_nathan()

    def run_test(self):
        self.s.create_contract(x86_64_contract = True, with_response = True)
        self.s.create_contract(x86_64_contract = False, with_response = True)
        uc = utillization_checker([self.d.get_addresses()[1]], ["echonode1"])
        uc.run_check()
        tc = tps_checker(self.d.get_addresses()[0], self.tx_count * self.cycles)
        tc.run_check()
        for i in range(self.cycles):
            self.s.transfer(int(self.tx_count * tx_ratio.transfer))
            self.s.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = True)
            self.s.call_contract(contract_id = "1.11.0", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = True)
            self.s.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = False)
            self.s.call_contract(contract_id = "1.11.1", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = False)
        tc.wait_check()
        uc.stop_check()
