import threading
from time import sleep

from .node_deployer.deployer import deployer
from .node_deployer.utilization_checker import utillization_checker
from .node_deployer.tps_checker import tps_checker
from .node_sender.sender import Sender
from .utils.utils import tx_ratio

class load_test:
    def __init__(self, node_count, echo_bin, image, pumba_bin, delay_time, conn_type, tx_count = 10, cycles = 1):
        self.tx_count = tx_count
        self.cycles = cycles
        self.node_count = node_count
        self.d = deployer(echo_bin=echo_bin, pumba_bin=pumba_bin, node_count=node_count, image=image, conn_type=conn_type)

        nodes_names = self.get_nodes_names()
        self.d.run_pumba(nodes_names, delay_time, 0)

        self.d.wait_nodes()

    def get_nodes_names(self):
        nodes_names = ""

        for i in range(self.node_count):
            nodes_names = nodes_names + " " + "echonode" + str(i)

        return nodes_names

    def send_set(self, sender):
        for i in range(self.cycles):
            sender.transfer(int(self.tx_count * tx_ratio.transfer))
            sender.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = True)
            sender.call_contract(contract_id = "1.11.0", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = True)
            sender.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = False)
            sender.call_contract(contract_id = "1.11.1", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = False)
            # sleep(self.tx_count * self.node_count / 100)
            sleep(2)

    def run_test(self):
        senders_list = []
        number_of_node = 0
        for a in (self.d.get_addresses()):
            senders_list.append(Sender(a, (number_of_node * self.tx_count * ((self.cycles / 100) + (self.cycles % 1000)) + number_of_node * 5)))
            number_of_node += 1


        senders_list[0].import_balance_to_nathan()

        senders_list[0].create_contract(x86_64_contract = True, with_response = True)
        senders_list[0].create_contract(x86_64_contract = False, with_response = True)

        uc = utillization_checker([self.d.get_addresses()[1]], ["echonode1"])
        uc.run_check()
        tc = tps_checker(self.d.get_addresses()[0], self.tx_count * self.cycles * self.node_count)
        tc.run_check()

        threads_list = []

        for s in senders_list:
            t = threading.Thread(target=self.send_set, args=(s, ))
            threads_list.append(t)

        for t in threads_list:
            t.start()

        tc.wait_check()
        uc.stop_check()
        self.d.kill_pumba()