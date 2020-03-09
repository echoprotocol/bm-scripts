from .node_deployer.deployer import deployer
from .node_deployer.deployer import connect_type
from .node_deployer.propagation_checker import propagation_checker
from .node_sender.sender import Sender
from time import sleep

class propagation_test:
    def __init__(self, node_count, echo_bin, image, pumba_bin, delay, delayed_lst):
        self.d = deployer(node_count=node_count, echo_bin=echo_bin, image=image,
                          conn_type = connect_type.serial, pumba_bin = pumba_bin)
        print("Delay in test", delay,"ms")
        if not delayed_lst:
            self.d.run_pumba(self.node_names(self.d.node_names), delay, 0)
        else:
            self.d.run_pumba(self.node_names(delayed_lst), delay, 0)
        self.d.wait_nodes()
        self.s = Sender(self.d.get_addresses()[0])
        self.s.import_balance_to_nathan()

    def node_names(self, lst):
        dnodes = " ".join(str(name) for name in lst)
        print("Delayed nodes:", dnodes)
        return dnodes

    def run_test(self):
        pc1 = propagation_checker(self.d.get_addresses()[0])
        pc2 = propagation_checker(self.d.get_addresses()[-1])
        for i in range(5):
            self.tx = self.s.create_transfer_transaction()
            pc1.run_check(self.tx)
            pc2.run_check(self.tx)
            self.s.echo_ops.broadcast(self.tx, with_response = False)
            pc1.wait_check()
            pc2.wait_check()
            print("Propagation time: ", pc2.get_time() - pc1.get_time())
        self.d.kill_pumba()