import threading
from time import sleep

from .node_deployer.deployer import deployer
from .node_deployer.utilization_checker import utillization_checker
from .node_deployer.tps_checker import tps_checker
from .node_sender.sender import Sender
from .utils.utils import tx_ratio

class load_test:
    def __init__(self, node_count, without_docker, echo_bin, image, pumba_bin, delay_time, conn_type, tx_count = 10, cycles = 1):
        try:
            self.d = None
            self.is_interrupted = False
            self.tx_count = tx_count
            self.cycles = cycles
            self.node_count = node_count
            self.without_docker = without_docker
            self.d = deployer(echo_bin=echo_bin, pumba_bin=pumba_bin, node_count=node_count, image=image,
                              conn_type=conn_type, without_docker=without_docker)
            nodes_names = self.get_nodes_names()
            if delay_time != 0:
                print("Delay in test", delay_time,"ms")
                self.d.run_pumba(nodes_names, delay_time, 0)
            self.d.wait_nodes()
        except Exception as e:
            if self.d is not None:
                self.d.kill_pumba()
                self.d.stop_containers()
            raise e

    def get_nodes_names(self):
        nodes_names = ""

        for i in range(self.node_count):
            nodes_names = nodes_names + " " + "echonode" + str(i)

        return nodes_names

    def send_set(self, sender):
        i = 0
        while self.is_interrupted == False and i < self.cycles:
            sender.transfer(int(self.tx_count * tx_ratio.transfer))
            sender.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = True)
            sender.call_contract(contract_id = "1.11.0", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = True)
            sender.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = False)
            sender.call_contract(contract_id = "1.11.1", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = False)
            sleep(2)
            i += 1

    def run_test(self):
        senders_list = []
        for i in range(self.node_count):
            senders_list.append(Sender(self.d.get_addresses()[i], self.d.get_rps_ports()[i], (i * self.tx_count * self.cycles + i)))


        senders_list[0].import_balance_to_nathan()

        senders_list[0].create_contract(x86_64_contract = True, with_response = True)
        senders_list[0].create_contract(x86_64_contract = False, with_response = True)

        if self.without_docker == False:
            self.uc = utillization_checker([self.d.get_addresses()[1]], [self.d.get_ports()[1]], ["echonode1"])
            self.uc.run_check()
        self.tc = tps_checker(self.d.get_addresses()[0], self.d.get_rps_ports()[0], self.tx_count * self.cycles * self.node_count)
        self.tc.run_check()

        self.threads_list = []

        for s in senders_list:
            t = threading.Thread(target=self.send_set, args=(s, ))
            self.threads_list.append(t)

        for t in self.threads_list:
            t.start()

        self.tc.wait_check()
        if self.without_docker == False:
            self.uc.stop_check()
        self.d.kill_pumba()
        for t in self.threads_list:
            t.join()

    def stop_checkers(self):
        self.is_interrupted = True
        for t in self.threads_list:
            t.join()
        self.tc.interrupt_checker()
        if self.without_docker == False:
            self.uc.interrupt_checker()
