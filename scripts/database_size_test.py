from time import sleep

from .node_deployer.deployer import deployer
from .node_deployer.utilization_checker import utilization_checker
from .node_deployer.tps_checker import tps_checker
from .node_sender.sender import Sender
from .utils.utils import tx_ratio


class database_size_test:
    def __init__(
        self, node_count, echo_bin, image, comm_count, tx_count=1000, cycles=1
    ):
        try:
            self.tx_count = tx_count
            self.cycles = cycles
            self.d = deployer(
                node_count=node_count,
                echo_bin=echo_bin,
                image=image,
                committee_count=comm_count,
            )
            self.d.wait_nodes()
            self.s = Sender(self.d.get_addresses()[0], self.d.rpc_ports[0])
            self.s.import_balance_to_nathan()
            self.s.balance_distribution()
        except Exception as e:
            if self.d is not None:
                self.d.kill_pumba()
                self.d.stop_containers()
            raise e

    def run_test(self):
        self.s.create_contract(x86_64_contract=True, with_response=True)
        self.s.create_contract(x86_64_contract=False, with_response=True)
        self.uc = utilization_checker(
            [self.d.get_addresses()[1]], [self.d.ports[1]], ["echonode1"]
        )
        self.uc.run_check()
        self.tc = tps_checker(
            self.d.get_addresses()[0], self.d.rpc_ports[0], self.tx_count * self.cycles
        )
        self.tc.run_check()
        transfer_txs = int(self.tx_count * tx_ratio.transfer)
        create_txs = int(self.tx_count * tx_ratio.create_contract / 2)
        call_txs = int(self.tx_count * tx_ratio.call_contract / 2)
        collected = 0
        for i in range(self.cycles):
            collected += self.s.transfer(transfer_txs)
            collected += self.s.create_contract(
                transaction_count=create_txs, x86_64_contract=True
            )
            collected += self.s.call_contract(
                contract_id="1.11.0", transaction_count=call_txs, x86_64_contract=True
            )
            collected += self.s.create_contract(
                transaction_count=create_txs, x86_64_contract=False
            )
            collected += self.s.call_contract(
                contract_id="1.11.1", transaction_count=call_txs, x86_64_contract=False
            )
        self.tc.sent_tx_number = collected
        self.s.interrupt_sender()
        self.tc.wait_check()
        self.uc.stop_check()

    def stop_checkers(self):
        self.s.interrupt_sender()
        self.tc.interrupt_checker()
        self.uc.interrupt_checker()
