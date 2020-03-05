#!/usr/bin/python3

import os
import time
import psutil
import threading
from .deployer import client 

class utillization_checker:
    def __init__(self, addresses = [], names = []):
        self.addrs = addresses
        self.names = names
        self.pids = []
        self.files = []
        self.containers = []
        self.set_pids()
        self.set_containers()
        self.prepare_files()

    def set_pids(self):
        base = "--p2p-endpoint={}:{}"
        for addr in self.addrs:
            for proc in psutil.process_iter():
                if (proc.name() == "echo_node" and
                    base.format(addr, 13375) in proc.cmdline()):
                        self.pids.append(proc.pid)

    def set_containers(self):
        for name in self.names:
            self.containers.append(client.containers.get(name))

    def prepare_files(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        dir = dir + "/../../results"
        if not os.path.exists(dir):
            os.makedirs(dir)

        dir = dir + "/{}/".format(os.getpid())
        if not os.path.exists(dir):
            os.makedirs(dir)

        for name in self.names:
            self.files.append(open(dir+name+".txt","w+"))

    def collect_stats(self):
        base = "du -sb /tmp/echorand_test_datadir/{}/blockchain"
        while (self.is_running):
            for i, pid in zip(range(0, len(self.pids)), self.pids):
                process = psutil.Process(pid)
                rssize = process.memory_info().rss
                vmsize = process.memory_info().vms
                bytes = self.containers[i].exec_run(base.format(self.names[i]) + "/database").output
                dbsize = bytes.decode('utf-8').split('\t')[0]
                bytes = self.containers[i].exec_run(base.format(self.names[i]) + "/x86_vm").output
                x86size = bytes.decode('utf-8').split('\t')[0]
                bytes = self.containers[i].exec_run(base.format(self.names[i]) + "/evm").output
                evmsize = bytes.decode('utf-8').split('\t')[0]
                print(rssize, vmsize, dbsize, x86size, evmsize)
                self.files[i].write("%d  %d  %s  %s  %s\n" % (rssize, vmsize, dbsize, x86size, evmsize))
            time.sleep(20)

    def run_check(self):
        self.is_running = True
        self.t = threading.Thread(target=self.collect_stats)
        self.t.start()
        print("Started utilization checker - Done")

    def stop_check(self):
        self.is_running = False
        self.t.join()
        for file in self.files:
            file.close()
        print("Utilization checker results:", os.getpid())

#def test():
#    d = deployer(node_count=2, echo_bin="/home/pplex/echo/build/bin/echo_node", pumba_bin="/home/pplex/pumba/.bin/pumba", image="ubuntu_delay")
#    u = utillization_checker(d.get_addresses(), d.get_node_names())
#    u.run_check()
#    time.sleep(120)
#    u.stop_check()
#test()
