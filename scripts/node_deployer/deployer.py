#!/usr/bin/python3

import os
import docker
import tarfile
import socket
import signal
import time
import tempfile
import subprocess

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
                 conn_type = connect_type.all_to_all):
        self.delayed_nodes=[]
        self.node_names=[]
        self.inverse_delayed_nodes=[]
        self.addresses=[]
        self.seed_node_args=[]
        self.account_info_args=[]
        self.launch_strs=[]

        self.pumba_bin = pumba_bin
        self.echo_bin = echo_bin
        self.echo_data_dir = "./tmp/echorand_test_datadir"
        self.image = image

        self.port = 13375
        self.rpc_port = 8090
        self.node_count = node_count
        self.conn_type = conn_type

        self.set_node_names()
        self.stop_containers() # stop before start if not stopped in previous run
        self.start_contrainers()
        self.set_node_addresses()
        self.set_seed_node_args()
        self.set_account_info_args()
        self.copy_data()
        self.set_launch_args()
        self.start_nodes()

    def set_node_names(self):
        for i in range(self.node_count):
            self.node_names.append("echonode{}".format(i))

    def set_node_addresses(self):
        for name in self.node_names:
            container = client.containers.get(name)
            self.addresses.append(container.attrs['NetworkSettings']['IPAddress'])

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
            base = "./echo_node --data-dir={datadir}/{dir} {p2p} {rpc} --genesis-json private_genesis.json {acc_infos} --start-echorand"
        else:
            base = "./echo_node --data-dir={datadir}/{dir} {p2p} {rpc} --genesis-json private_genesis.json {acc_infos} --start-echorand --config-seeds-only"
        for i in range(self.node_count):
            rpc="--rpc-endpoint={}:{}".format(self.addresses[i], self.rpc_port)
            p2p="--p2p-endpoint={}:{} {}".format(self.addresses[i], self.port, self.seed_node_args[i])
            self.launch_strs.append(base.format(datadir=self.echo_data_dir, dir=self.node_names[i], dnum=i, p2p=p2p, rpc=rpc, acc_infos=self.account_info_args[i]))

    def form_serial_connection(self):
        self.seed_node_args.append("")
        for i in range(1, self.node_count):
            self.seed_node_args.append("--seed-node={}:{}".format(self.addresses[i-1], self.port))

    def form_circlular_connection(self):
        self.seed_node_args.append("")
        for i in range(1, self.node_count):
            self.seed_node_args.append("--seed-node={}:{}".format(self.addresses[i-1], self.port))
        self.seed_node_args[0]="--seed-node={}:{}".format(self.addresses[self.node_count-1], self.port)

    def form_all_to_all_connection(self):
        for i in range(0, self.node_count):
            seed_args = ""
            for j in range(0, self.node_count):
                if (i != j):
                    seed_args = seed_args + ("--seed-node={}:{} ".format(self.addresses[j], self.port))
            self.seed_node_args.append(seed_args)

    def copy_to(self, dst, *args):
        name, dst = dst.split(':')
        container = client.containers.get(name)
        for src in args:
            with simple_tar(src) as tar_file:
                container.put_archive(os.path.dirname(dst), tar_file)

    def copy_data(self):
        for name in self.node_names:
            self.copy_to("{}:/".format(name), "../resources/access.json", "../resources/private_genesis.json")
            self.copy_to("{}:/echo_node".format(name), self.echo_bin)

    def start_nodes(self):
        container = client.containers.get(self.node_names[0])
        cmd = "/bin/sh -c '{}'".format(self.launch_strs[0])
        container.exec_run(cmd, detach=True)
        for i in range(1, self.node_count):
            container = client.containers.get(self.node_names[i])
            cmd = "/bin/sh -c '{}'".format(self.launch_strs[i])
            while (self.conn_type != connect_type.all_to_all and self.node_is_not_started(self.addresses[i-1])):
                time.sleep(1)
            container.exec_run(cmd, detach=True)

    def start_contrainers(self):
        for name in self.node_names:
            container = client.containers.run(self.image,\
                detach=True,name=name,remove=True,tty=True)

    def stop_containers(self):
        for name in self.node_names:
            try:
                container = client.containers.get(name)
                container.stop()
            except:
                pass

    def node_is_not_started(self, addr): # return true if node is not started yet
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((addr, self.rpc_port))
        sock.close()
        return result

    def get_addresses(self):
        return self.addresses

    def get_node_names(self):
        return self.node_names

    def run_pumba(self, nodes, time, jitter):
        cmd = "{pumba_bin} netem --interface=eth0 --duration 90m delay --time {time} --jitter {jitter} --correlation 0 {containers}"
        self.pumba_proc = subprocess.Popen(cmd.format(pumba_bin=self.pumba_bin,
            time=time, jitter=jitter, containers = nodes), shell=True, preexec_fn=os.setsid)

    def kill_pumba(self):
        os.killpg(os.getpgid(self.pumba_proc.pid), signal.SIGTERM)

def test():
    d = deployer(node_count=2, echo_bin="/home/pplex/echo/build/bin/echo_node", pumba_bin="/home/pplex/pumba/.bin/pumba", image="ubuntu_delay")
    nodes = "echonode0 echonode1"
    d.run_pumba(nodes, 500, 10)
    time.sleep(30)
    d.kill_pumba()
    #d.stop_containers()

#test()
