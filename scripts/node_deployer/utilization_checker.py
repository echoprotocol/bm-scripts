#!/usr/bin/python3

import os
import time
import psutil
import threading
from .deployer import client 
from datetime import datetime

class utilization_checker:
    def __init__(self, addresses = [], ports = [], names = [], volume_dir=""):
        self.addrs = addresses
        self.ports = ports
        self.names = names
        self.pids = []
        self.nums = []
        self.files = []
        self.is_running = False
        self.volume_dir = volume_dir
        self.set_pids()
        self.prepare_files()

    def set_pids(self):
        base = "--p2p-endpoint={}:{}"
        for i in range(len(self.addrs)):
            for proc in psutil.process_iter():
                if (proc.name() == "echo_node" and
                    base.format(self.addrs[i], self.ports[i]) in proc.cmdline()):
                        self.pids.append(proc.pid)
                        self.nums.append(i)

    def prepare_files(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        dir = dir + "/../../results"
        if not os.path.exists(dir):
            os.makedirs(dir)

        dir = dir + "/{}/".format(os.getpid())
        print("uchecker results will be placed at \"/results/%d/\"" % os.getpid(), flush=True)
        if not os.path.exists(dir):
            os.makedirs(dir)

        for name in self.names:
            self.files.append(open(dir+name+".txt","w+"))

    def collect_stats(self):
        base = "du -sb "+self.volume_dir+"/echorand_test_datadir/{}/blockchain"
        names = [self.names[i] for i in self.nums]
        print("Collection statistics for", names)
        self.is_running = True
        for file in self.files:
            file.write("time,       rssize,      vmsize,      cpu,     dbsize,    x86size,    evmsize\n\n")

        try:
            while (self.is_running):
                for i, pid in zip(self.nums, self.pids):
                    process = psutil.Process(pid)
                    rssize = process.memory_info().rss
                    vmsize = process.memory_info().vms
                    cpu = process.cpu_percent(interval=1)
                    bytes = os.popen(base.format(self.names[i])+"/database").read()
                    dbsize = bytes.split('\t')[0]
                    bytes = os.popen(base.format(self.names[i])+"/x86_vm").read()
                    x86size = bytes.split('\t')[0]
                    bytes = os.popen(base.format(self.names[i])+"/evm").read()
                    evmsize = bytes.split('\t')[0]
                    t = datetime.now().strftime("%H:%M:%S")
                    self.files[i].write("%s   %d    %d   %f   %s      %s        %s\n" % (t, rssize, vmsize, cpu, dbsize, x86size, evmsize))
                    self.files[i].flush()
                time.sleep(20)
        except (FileNotFoundError, psutil._exceptions.NoSuchProcess) as e:
            self.is_running = False

    def run_check(self):
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
