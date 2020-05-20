from .node_deployer.deployer import deployer
from .node_deployer.deployer import connect_type
from .node_deployer.utilization_checker import utilization_checker
from .node_deployer.tps_checker import tps_checker
from .node_sender.sender import Sender


class tps_test:
    def __init__(
        self,
        node_count,
        echo_bin,
        pumba_bin,
        image,
        tx_count,
        delay=0,
        delayed_lst=[],
        tx_case=0,
        conn_type=connect_type.serial,
        comm_count=20,
    ):
        try:
            self.tc = None
            self.uc = None
            self.d = None
            self.tx_count = tx_count
            self.delay = delay
            self.tx_case = tx_case
            self.d = deployer(
                node_count=node_count,
                echo_bin=echo_bin,
                pumba_bin=pumba_bin,
                image=image,
                conn_type=conn_type,
                committee_count=comm_count,
            )
            if self.delay != 0:
                print("Delay in test", delay, "ms")
                if not delayed_lst:
                    self.d.run_pumba(self.node_names(self.d.node_names), self.delay, 0)
                else:
                    self.d.run_pumba(self.node_names(delayed_lst), self.delay, 0)
            self.d.wait_nodes()
            self.s = Sender(
                self.d.get_addresses()[0], self.d.rpc_ports[0], self.d.committee_count
            )
            self.s.import_balance_to_nathan()
            self.s.balance_distribution()
            self.sent_txs = 0
        except Exception as e:
            if self.d is not None:
                self.d.kill_pumba()
                self.d.stop_containers()
            raise e

    def node_names(self, lst):
        dnodes = " ".join(str(name) for name in lst)
        print("Delayed nodes:", dnodes)
        return dnodes

    def run_transfer_case(self):
        print("Started transfer case,", "transaction count -", self.tx_count)
        self.tc = tps_checker(
            self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count
        )
        self.tc.run_check()
        self.sent_txs = self.s.transfer(self.tx_count)
        self.tc.sent_tx_number = self.sent_txs

    def run_create_evm_case(self):
        print("Started create evm case,", "transaction count -", self.tx_count)
        self.tc = tps_checker(
            self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count
        )
        self.tc.run_check()
        self.sent_txs = self.s.create_contract(
            transaction_count=self.tx_count, x86_64_contract=False
        )
        self.tc.sent_tx_number = self.sent_txs

    def run_call_emv_case(self):
        print("Started call evm case,", "transaction count -", self.tx_count)
        self.s.create_contract(x86_64_contract=False, with_response=True)
        self.tc = tps_checker(
            self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count
        )
        self.tc.run_check()
        self.sent_txs = self.s.call_contract(
            contract_id="1.11.0", transaction_count=self.tx_count, x86_64_contract=False
        )
        self.tc.sent_tx_number = self.sent_txs

    def run_create_x86_case(self):
        print("Started create x86 case,", "transaction count -", self.tx_count)
        self.tc = tps_checker(
            self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count
        )
        self.tc.run_check()
        self.sent_txs = self.s.create_contract(
            transaction_count=self.tx_count, x86_64_contract=True
        )
        self.tc.sent_tx_number = self.sent_txs

    def run_call_x86_case(self):
        print("Started call x86 case,", "transaction count -", self.tx_count)
        self.s.create_contract(x86_64_contract=True, with_response=True)
        self.tc = tps_checker(
            self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count
        )
        self.tc.run_check()
        self.sent_txs = self.s.call_contract(
            contract_id="1.11.0", transaction_count=self.tx_count, x86_64_contract=True
        )
        self.tc.sent_tx_number = self.sent_txs - 1

    def run_case(self):
        casemap = {
            0: self.run_transfer_case,
            1: self.run_create_evm_case,
            2: self.run_call_emv_case,
            3: self.run_create_x86_case,
            4: self.run_call_x86_case,
        }
        casemap[self.tx_case]()

    def run_test(self):
        self.uc = utilization_checker(
            self.d.get_addresses(), self.d.ports, self.d.get_node_names()
        )
        self.uc.run_check()
        self.run_case()
        self.s.interrupt_sender()
        self.tc.wait_check()
        self.uc.stop_check()
        self.d.kill_pumba()

    def stop_checkers(self):
        self.s.interrupt_sender()
        self.tc.interrupt_checker()
        self.uc.interrupt_checker()
