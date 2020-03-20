import threading
from time import sleep

from .node_deployer.deployer import deployer
from .node_deployer.utilization_checker import utilization_checker
from .node_deployer.tps_checker import tps_checker
from .node_sender.sender import Sender
from .utils.utils import tx_ratio

class load_test:
    def __init__(self, node_count, echo_bin, image, pumba_bin, delay_time, conn_type, tx_count = 10, cycles = 1):
        try:
            self.d = None
            self.is_interrupted = False
            self.tx_count = tx_count
            self.cycles = cycles
            self.node_count = node_count
            self.d = deployer(echo_bin=echo_bin, pumba_bin=pumba_bin, node_count=node_count, image=image, conn_type=conn_type)
            nodes_names = self.get_nodes_names()
            if delay_time != 0:
                print("Delay in test", delay_time,"ms")
                self.d.run_pumba(nodes_names, delay_time, 0)
            self.d.wait_nodes()
            self.sent_txs=0
            self.lock=threading.Lock()
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

    def increase_sent_txs(self, value):
        self.lock.acquire()
        self.sent_txs = self.sent_txs + value
        self.lock.release()

    def send_set(self, sender):
        i = 0
        transfer_txs = int(self.tx_count * tx_ratio.transfer)
        create_txs= int(self.tx_count * tx_ratio.create_contract / 2)
        call_txs = int(self.tx_count * tx_ratio.call_contract / 2)
        while self.is_interrupted == False and i < self.cycles:
            sender.transfer(int(self.tx_count * tx_ratio.transfer))
            sender.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = True)
            sender.call_contract(contract_id = "1.11.0", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = True)
            sender.create_contract(transaction_count = (int(self.tx_count * tx_ratio.create_contract / 2)), x86_64_contract = False)
            sender.call_contract(contract_id = "1.11.1", transaction_count = (int(self.tx_count * tx_ratio.call_contract / 2)), x86_64_contract = False)
            sleep(2)
            i += 1
            self.increase_sent_txs(transfer_txs+create_txs*2+call_txs*2)
            print("Sent txs", self.sent_txs)

    def run_test(self):
        senders_list = []
        number_of_node = 0
        for a,p in zip(self.d.get_addresses(), self.d.rpc_ports):
            senders_list.append(Sender(a,p, (number_of_node * self.tx_count * ((self.cycles / 100) + (self.cycles % 1000)) + number_of_node * 5)))
            number_of_node += 1


        senders_list[0].import_balance_to_nathan()

        senders_list[0].create_contract(x86_64_contract = True, with_response = True)
        senders_list[0].create_contract(x86_64_contract = False, with_response = True)

        self.uc = utilization_checker([self.d.get_addresses()[1]], [self.d.ports[1]], ["echonode1"])
        self.uc.run_check()
        self.tc = tps_checker(self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count*self.cycles*self.node_count)
        self.tc.run_check()

        self.threads_list = []

        for s in senders_list:
            t = threading.Thread(target=self.send_set, args=(s, ))
            self.threads_list.append(t)

        for t in self.threads_list:
            t.start()

        for t in self.threads_list:
            t.join()
        self.tc.sent_tx_number = self.sent_txs

        self.tc.wait_check()
        self.uc.stop_check()
        self.d.kill_pumba()

    def stop_checkers(self):
        self.is_interrupted = True
        for t in self.threads_list:
            t.join()
        self.tc.interrupt_checker()
        self.uc.interrupt_checker()
