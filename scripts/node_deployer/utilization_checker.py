#!/usr/bin/python3

import os
import time
import psutil
import threading
from .deployer import client 
from .tps_checker import tps_checker

class utilization_checker:
    def __init__(self, addresses = [], ports = [], names = []):
        self.addrs = addresses
        self.ports = ports
        self.names = names
        self.pids = []
        self.nums = []
        self.files = []
        self.containers = []
        self.set_pids()
        self.set_containers()
        self.prepare_files()

    def set_pids(self):
        base = "--p2p-endpoint={}:{}"
        for i in range(len(self.addrs)):
            for proc in psutil.process_iter():
                if (proc.name() == "echo_node" and
                    base.format(self.addrs[i], self.ports[i]) in proc.cmdline()):
                        self.pids.append(proc.pid)
                        self.nums.append(i)

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
        names = [self.names[i] for i in self.nums]
        print("Collection statistics for", names)
        while (self.is_running):
            for i, pid in zip(self.nums, self.pids):
                block_number = tps_checker.get_block_number()
                process = psutil.Process(pid)
                rssize = process.memory_info().rss
                vmsize = process.memory_info().vms
                cpu = process.cpu_percent(interval=1)
                bytes = self.containers[i].exec_run(base.format(self.names[i]) + "/database").output
                dbsize = bytes.decode('utf-8').split('\t')[0]
                bytes = self.containers[i].exec_run(base.format(self.names[i]) + "/x86_vm").output
                x86size = bytes.decode('utf-8').split('\t')[0]
                bytes = self.containers[i].exec_run(base.format(self.names[i]) + "/evm").output
                evmsize = bytes.decode('utf-8').split('\t')[0]
                self.files[i].write("%d %d  %d  %f  %s  %s  %s\n" % (block_number, rssize, vmsize, cpu, dbsize, x86size, evmsize))
                self.files[i].flush()
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

    def interrupt_checker(self):
        print("Waiting utilization checker...")
        self.stop_check()
