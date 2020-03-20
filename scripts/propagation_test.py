from .node_deployer.deployer import deployer
from .node_deployer.deployer import connect_type
from .node_deployer.propagation_checker import propagation_checker
from .node_sender.sender import Sender
from time import sleep

class propagation_test:
    def __init__(self, node_count, echo_bin, image, pumba_bin, delay, delayed_lst):
        try:
            self.pc1 = None
            self.pc2 = None
            self.delay = delay
            self.d = deployer(node_count=node_count, echo_bin=echo_bin, image=image,
                              conn_type = connect_type.serial, pumba_bin = pumba_bin)
            if self.delay != 0:
                print("Delay in test", delay,"ms")
                if not delayed_lst:
                    self.d.run_pumba(self.node_names(self.d.node_names), delay, 0)
                else:
                    self.d.run_pumba(self.node_names(delayed_lst), delay, 0)
            self.d.wait_nodes()
            self.s = Sender(self.d.get_addresses()[0], self.d.rpc_ports[0])
            self.s.import_balance_to_nathan()
        except Exception as e:
            if self.d is not None:
                self.d.kill_pumba()
                self.d.stop_containers()
            raise e

    def node_names(self, lst):
        dnodes = " ".join(str(name) for name in lst)
        print("Delayed nodes:", dnodes)
        return dnodes

    def run_test(self):
        self.pc1 = propagation_checker(self.d.get_addresses()[0], self.d.rpc_ports[0])
        self.pc2 = propagation_checker(self.d.get_addresses()[-1], self.d.rpc_ports[-1])
        for i in range(5):
            self.tx = self.s.create_transfer_transaction()
            self.pc1.run_check(self.tx)
            self.pc2.run_check(self.tx)
            self.s.echo_ops.broadcast(self.tx, with_response = False)
            self.pc1.wait_check()
            self.pc2.wait_check()
            print("Propagation time: ", self.pc2.get_time() - self.pc1.get_time())
        self.d.kill_pumba()

    def stop_checkers(self):
       if self.pc1 is not None:
            self.pc1.interrupt_checker()
       if self.pc2 is not None:
            self.pc2.interrupt_checker()
