#!/usr/bin/python3

import os
import subprocess
import docker
import tarfile
import socket
import signal
import time
import tempfile
import subprocess
import sys

from pathlib import Path

from ..utils.files_path import RESOURCES_DIR

DETACHED_PROCESS = 0x00000008

COMMITTEE_COUNT=20
PRIVATE_KEYS = ["5KBPWjxKz8Ym7CLatFMa5XtfbvTzEt7vMugkRNk7go9dBQfJLYt",
                "5JdPusf39CuwYWnvzJX7JnBtUdkqzWqfVE9WBfkqSye8BC5nyzh",
                "5Hvvh3Sj6GRMCzeAk965QhxurYzpAcLVALvBCciW73Q9KeTwK8e",
                "5KUphcsPV2s7sGCksLZ9u9GSUGezJ83E4w6LVxoCeMEdAuFAdRw",
                "5KAPbigUUgog3DB8BfY3jJbrsknzAWjf4gzvbpZrvoguLjcfGmr",
                "5JLpiU7J5WNUHimq8samGBupbc3MdRg63ufyEcarzQKyyn4iiEm",
                "5JGvwKpj3zZbZKxWpMNT7qVNi489Peq58nQhFdUzZUqPcbLnpCs",
                "5JB3K8TgAowtxV6HBsLqrKkkuxLW3DV94uSXgPZhapNuWi9zoEB",
                "5KZq5vzfgphdTv9uAEmWzMu6GuzZqkNicBHGRhCxPSnTCeArTbf",
                "5Jz4sZPSnG4D7yYrW5kvXpvJkXqH16F9A8DFeume4EiJomN6oYL",
                "5KXp7WBiPPFE44QSBgNzEqjqgamkTXn5tT4cCctoFb4zVL3HFpn",
                "5JkoodR3pMMXLRcMhrqSMNgE5mrhVemPVqvGaigRNskSf7e9T11",
                "5HzGZZSXJmTkzf5FGoyaqjR1nsBTk8vEskjHkxUiwt8DaMXQq91",
                "5KfWnaGesmyXVuzMjidr1UNLaoVxmTQpeWJUATXogTizckGmg4j",
                "5HqDbVtVM8qZXr2wEyxeCQHHCr55bRDFhSPitBiYk5gdFgBjVbu",
                "5JmoKXdyVERZXgMpXm1FyzkFWRmnh678v6GZNFQGZNecxgkQWnw",
                "5JAKxW1ZkFiCTJUjgBnhJZFWyGYD5e7uoiCDZ1UZQffSjK5J9Zf",
                "5HtswsUqHURnTGTpuqTb9gFAASkKHR48CLRThLVZ8PKqiQ8P9aK",
                "5KGyuPZoApBbQSbSegZXKp5D4ajqDmoQx1jumt6UZXpVfV56oRB",
                "5JjHQ1GqTbqVZLdTB3QRqcUWA6LezqA65iPJbq5craE6MRc4u9K"
               ]

NATHAN_PRIV="5JjHQ1GqTbqVZLdTB3QRqcUWA6LezqA65iPJbq5craE6MRc4u9K"

def simple_tar(path):
    f = tempfile.NamedTemporaryFile()
    t = tarfile.open(mode='w', fileobj=f)

    abs_path = os.path.abspath(path)
    t.add(abs_path, arcname=os.path.basename(path), recursive=False)

    t.close()
    f.seek(0)
    return f

from enum import Enum
class connect_type(Enum):
    serial = 1
    circular = 2
    all_to_all = 3

client = docker.from_env()

class deployer:
    def __init__(self, echo_bin="", pumba_bin="", node_count = 2, image = "",\
                 conn_type = connect_type.all_to_all, without_docker = False):
        self.delayed_nodes=[]
        self.node_names=[]
        self.inverse_delayed_nodes=[]
        self.addresses=[]
        self.seed_node_args=[]
        self.account_info_args=[]
        self.launch_strs=[]

        self.pumba_bin = pumba_bin
        self.echo_bin = echo_bin
        self.echo_data_dir = "./tmp2/echorand_test_datadir"
        self.image = image
        self.pumba_started = False

        self.ports = [13375]
        self.rpc_ports = [8090]
        self.node_count = node_count
        self.conn_type = conn_type

        self.without_docker = without_docker

        self.set_node_names()
        self.stop_containers() # stop before start if not stopped in previous run
        if without_docker == False:
            self.start_contrainers()
        self.set_node_addresses()
        self.set_node_ports()
        self.set_seed_node_args()
        self.set_account_info_args()
        if without_docker == False:
            self.copy_data()
        self.set_launch_args()
        if without_docker == True:
            self.start_nodes_without_container()
        else:
            self.start_nodes_with_container()

    def set_node_names(self):
        for i in range(self.node_count):
            self.node_names.append("echonode{}".format(i))

    def set_node_addresses(self):
        if self.without_docker == True:
            for i in range(self.node_count):
                self.addresses.append("127.0.0.1")
        else:
            for name in self.node_names:
                container = client.containers.get(name)
                self.addresses.append(container.attrs['NetworkSettings']['IPAddress'])

    def set_node_ports(self):
        for i in range(1, self.node_count):
            if self.without_docker == True:
                self.ports.append(self.ports[0]+i)
                self.rpc_ports.append(self.rpc_ports[0]+i)
            else:
                self.ports.append(self.ports[0])
                self.rpc_ports.append(self.rpc_ports[0])

    def set_seed_node_args(self):
        if (self.conn_type == connect_type.serial):
            self.form_serial_connection()
        elif (self.conn_type == connect_type.circular):
            self.form_circlular_connection()
        elif (self.conn_type == connect_type.all_to_all):
            self.form_all_to_all_connection()

    def set_account_info_args(self):
        account_str = "--account-info \[\\\"1.2.{}\\\",\\\"{}\\\"\] "
        extra_str = "--plugins=registration --registrar-account=\\\"1.2.{}\\\" --api-access=./access.json"
        if COMMITTEE_COUNT > self.node_count:
            committee_per_node = int(COMMITTEE_COUNT / self.node_count)
            for i in range(self.node_count-1):
                account_args = ""
                for j in range(i*committee_per_node, (i+1)*committee_per_node):
                    account_args = account_args + account_str.format(j+6,PRIVATE_KEYS[j])
                self.account_info_args.append(account_args + extra_str.format(i*committee_per_node + 6))
            account_args = ""
            for j in range((self.node_count-1)*committee_per_node, COMMITTEE_COUNT):
                account_args = account_args + account_str.format(j+6,PRIVATE_KEYS[j])
            self.account_info_args.append(account_args + extra_str.format((self.node_count-1)*committee_per_node + 6))
        else:
            for i in range(COMMITTEE_COUNT):
                account_args = account_str.format(i+6,PRIVATE_KEYS[i])
                self.account_info_args.append(account_args + extra_str.format(i+6))
            for i in range(COMMITTEE_COUNT, self.node_count):
                self.account_info_args.append("--plugins=registration --api-access=./access.json")

    def set_launch_args(self):
        base = ""
        if (self.conn_type == connect_type.all_to_all):
            base = "HEAPPROFILE=tmp2/gperf_node{n}/heapprof ./echo_node --data-dir={datadir}/{dir} {p2p} {rpc} --genesis-json private_genesis.json {acc_infos} --start-echorand"
        else:
            base = "HEAPPROFILE=tmp2/gperf_node{n}/heapprof ./echo_node --data-dir={datadir}/{dir} {p2p} {rpc} --genesis-json private_genesis.json {acc_infos} --start-echorand --config-seeds-only"
        for i in range(self.node_count):
            rpc="--rpc-endpoint={}:{}".format(self.addresses[i], self.rpc_ports[i])
            p2p="--p2p-endpoint={}:{} {}".format(self.addresses[i], self.ports[i], self.seed_node_args[i])
            self.launch_strs.append(base.format(n=i, datadir=self.echo_data_dir, dir=self.node_names[i], dnum=i, p2p=p2p, rpc=rpc, acc_infos=self.account_info_args[i]))

            Path("tmp2/gperf_node{}".format(i)).mkdir(parents=True, exist_ok=True)

    def form_serial_connection(self):
        self.seed_node_args.append("")
        for i in range(1, self.node_count):
            self.seed_node_args.append("--seed-node={}:{}".format(self.addresses[i-1], self.ports[i-1]))

    def form_circlular_connection(self):
        self.seed_node_args.append("")
        for i in range(1, self.node_count):
            self.seed_node_args.append("--seed-node={}:{}".format(self.addresses[i-1], self.ports[i-1]))
        self.seed_node_args[0]="--seed-node={}:{}".format(self.addresses[self.node_count-1], self.ports[self.node_count-1])

    def form_all_to_all_connection(self):
        for i in range(0, self.node_count):
            seed_args = ""
            for j in range(0, self.node_count):
                if (i != j):
                    seed_args = seed_args + ("--seed-node={}:{} ".format(self.addresses[j], self.ports[j]))
            self.seed_node_args.append(seed_args)

    def copy_to(self, dst, *args):
        name, dst = dst.split(':')
        container = client.containers.get(name)
        for src in args:
            with simple_tar(src) as tar_file:
                container.put_archive(os.path.dirname(dst), tar_file)

    def copy_data(self):
        for name in self.node_names:
            self.copy_to("{}:/".format(name), RESOURCES_DIR+"/access.json", RESOURCES_DIR+"/private_genesis.json")
            self.copy_to("{}:/echo_node".format(name), self.echo_bin)

    def start_nodes_with_container(self):
        container = client.containers.get(self.node_names[0])
        cmd = "/bin/sh -c '{}'".format(self.launch_strs[0])
        container.exec_run(cmd, detach=True)
        for i in range(1, self.node_count):
            container = client.containers.get(self.node_names[i])
            cmd = "/bin/sh -c '{}'".format(self.launch_strs[i])
            while (self.conn_type != connect_type.all_to_all and self.node_is_not_started(i-1)):
                time.sleep(1)
            container.exec_run(cmd, detach=True)

    def start_nodes_without_container(self):
        cmd = self.launch_strs[0]
        log = open("tmp2/{}.txt".format(self.node_names[0]), "a")
        subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=log, stderr=log)
        for i in range(1, self.node_count):
            cmd = self.launch_strs[i]
            while (self.conn_type != connect_type.all_to_all and self.node_is_not_started(i-1)):
                time.sleep(1)
            log = open("tmp2/{}.txt".format(self.node_names[i]), "a")
            subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=log, stderr=log)

    def start_contrainers(self):
        for name in self.node_names:
            container = client.containers.run(self.image,\
                detach=True,name=name,remove=True,tty=True)

    def stop_containers(self):
        for name in self.node_names:
            try:
                container = client.containers.get(name)
                container.stop()
                container.remove()
            except:
                pass

    def node_is_not_started(self, n_node): # return true if node is not started yet
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((self.addresses[n_node], self.ports[n_node]))
        sock.close()
        return result

    def get_addresses(self):
        return self.addresses

    def get_ports(self):
        return self.ports

    def get_rps_ports(self):
        return self.rpc_ports

    def get_node_names(self):
        return self.node_names

    def run_pumba(self, nodes, time, jitter):
        self.pumba_started = True
        cmd = "{pumba_bin} netem --interface=eth0 --duration 90m delay --time {time} --jitter {jitter} --correlation 0 {containers}"
        self.pumba_proc = subprocess.Popen(cmd.format(pumba_bin=self.pumba_bin,
            time=time, jitter=jitter, containers = nodes), shell=True, preexec_fn=os.setsid)

    def wait_nodes(self):
        for i in range(self.node_count):
            while self.node_is_not_started(i):
                time.sleep(1)
        time.sleep(10) # unexplored behavior: without sleep node can crash during running
        print("Node deploying - Done")

    def kill_pumba(self):
        if self.pumba_started == True:
            os.killpg(os.getpgid(self.pumba_proc.pid), signal.SIGTERM)

def test():
    d = deployer(node_count=2, echo_bin="/home/pplex/echo/build/bin/echo_node", pumba_bin="/home/pplex/pumba/.bin/pumba", image="ubuntu_delay")
    nodes = "echonode0 echonode1"
    d.run_pumba(nodes, 500, 10)
    time.sleep(30)
    d.kill_pumba()
    #d.stop_containers()

#test()
