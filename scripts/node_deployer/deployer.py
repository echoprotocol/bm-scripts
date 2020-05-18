#!/usr/bin/python3

import os, shutil
import docker
import tarfile
import socket
import signal
import time
import tempfile
import subprocess
import sys
import socket
import json
from shutil import copy
from ..utils.files_path import RESOURCES_DIR
from ..utils.genesis_template import create_init_account, get_genesis_string
from ..utils.utils import generate_keys

COMMITTEE_COUNT = 20
NATHAN_PRIV = "5JjHQ1GqTbqVZLdTB3QRqcUWA6LezqA65iPJbq5craE6MRc4u9K"
NATHAN_PUB = "ECHO5NaRTkq4uBAVGrZkD3jcTEdUxhxxJLU7hvt3p1zJyytc"


def simple_tar(path):
    f = tempfile.NamedTemporaryFile()
    t = tarfile.open(mode="w", fileobj=f)

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
    def __init__(self, echo_bin="", pumba_bin="", node_count=2, image="",\
                 conn_type=connect_type.all_to_all, host_addresses=dict(), remote=False, start_node=0, account_info_args="", committee_count=20, volume_dir = "", clear_volume = True):
        self.delayed_nodes=[]
        self.node_names=[]
        self.inverse_delayed_nodes=[]
        self.addresses=[]
        self.ports=[]
        self.rpc_ports=[]
        self.seed_node_args=[]
        self.account_info_args=[]
        self.launch_strs=[]
        self.private_keys=[]
        self.public_keys=[]
        self.account_names=[]
        self.start_node=start_node

        self.pumba_bin = pumba_bin
        self.echo_bin = echo_bin
        self.echo_data_dir = "./tmp/echorand_test_datadir"
        self.image = image
        self.pumba_started = False
        self.host_ip = self.get_host_ip()
        self.host_addresses=self.remove_my_host(host_addresses)

        self.port = 13375
        self.rpc_port = 8090
        self.node_count = node_count
        self.conn_type = conn_type

        self.set_committee_count(committee_count)
        self.set_account_names()
        keys = generate_keys(self.committee_count)
        self.private_keys = keys[0]
        self.public_keys = keys[1]
        self.create_genesis()
        self.create_volume_dir(volume_dir, clear_volume)
        self.copy_log_configs(clear_volume)
        if remote == True:
            self.remote_deploying()
        else:
            self.local_deploying()

    def set_node_names(self):
        for i in range(self.node_count):
            self.node_names.append("echonode{}".format(i))

    def set_account_names(self):
        for i in range(self.committee_count - 1):
            self.account_names.append("init{}".format(i))
        self.account_names.append("nathan")

    def set_node_addresses(self):
        for name in self.node_names:
            container = client.containers.get(name)
            self.addresses.append(container.attrs["NetworkSettings"]["IPAddress"])

    def set_ports(self):
        for i in range(self.node_count):
            self.ports.append(self.port + i)
            self.rpc_ports.append(self.rpc_port + i)

    def set_seed_node_args(self):
        if self.conn_type == connect_type.serial:
            self.form_serial_connection()
        elif self.conn_type == connect_type.circular:
            self.form_circlular_connection()
        elif self.conn_type == connect_type.all_to_all:
            self.form_all_to_all_connection()

    def set_account_info_args(self):
        account_str = '--account-info \[\\"1.2.{}\\",\\"{}\\"\] '
        extra_str = '--plugins=registration --registrar-account=\\"1.2.{}\\" --api-access=./access.json'
        if self.committee_count > self.node_count:
            committee_per_node = int(self.committee_count / self.node_count)
            for i in range(self.node_count - 1):
                account_args = ""
                for j in range(i * committee_per_node, (i + 1) * committee_per_node):
                    account_args = account_args + account_str.format(
                        j + 6, self.private_keys[j]
                    )
                self.account_info_args.append(
                    account_args + extra_str.format(i * committee_per_node + 6)
                )
            account_args = ""
            for j in range(
                (self.node_count - 1) * committee_per_node, self.committee_count
            ):
                account_args = account_args + account_str.format(
                    j + 6, self.private_keys[j]
                )
            self.account_info_args.append(
                account_args
                + extra_str.format((self.node_count - 1) * committee_per_node + 6)
            )
        else:
            for i in range(self.committee_count):
                account_args = account_str.format(i + 6, self.private_keys[i])
                self.account_info_args.append(account_args + extra_str.format(i + 6))
            for i in range(self.committee_count, self.node_count):
                self.account_info_args.append(
                    "--plugins=registration --api-access=./access.json"
                )

    def set_remote_account_info_args(self):
        account_str = '--account-info \[\\"1.2.{}\\",\\"{}\\"\] '
        extra_str = '--plugins=registration --registrar-account=\\"1.2.{}\\" --api-access=./access.json'
        # extra_str = "--api-access=./access.json"

        servercount = (
            len(self.host_addresses) + 1
        )  # plus one due to my current host also should be counted
        accs_per_server = int(self.committee_count / servercount)
        accs_on_first_server = accs_per_server + self.committee_count % servercount
        start_pos = 0
        if self.start_node > 0:
            start_pos = accs_on_first_server + (self.start_node - 1) * accs_per_server
        if self.start_node == 0:
            accs_per_server = accs_on_first_server
        if accs_per_server < self.node_count:
            for i in range(accs_per_server):
                account_args = (
                    ""
                    + account_str.format(
                        i + start_pos + 6, self.private_keys[i + start_pos]
                    )
                    + extra_str.format(i + start_pos + 6)
                )
                self.account_info_args.append(account_args)
            for i in range(accs_per_server, self.node_count):
                # account_args = "" + extra_str.format(i+start_pos+6)
                account_args = "--api-access=./access.json"
                self.account_info_args.append(account_args)
        else:
            accs_per_node = int(accs_per_server / self.node_count)
            for i in range(self.node_count - 1):
                account_args = ""
                for j in range(i * accs_per_node, (i + 1) * accs_per_node):
                    account_args = account_args + account_str.format(
                        j + start_pos + 6, self.private_keys[j + start_pos]
                    )
                self.account_info_args.append(
                    account_args + extra_str.format(i * accs_per_node + start_pos + 6)
                )
            account_args = ""
            for j in range((self.node_count - 1) * accs_per_node, accs_per_server):
                account_args = account_args + account_str.format(
                    j + start_pos + 6, self.private_keys[j + start_pos]
                )
            self.account_info_args.append(
                account_args
                + extra_str.format(
                    (self.node_count - 1) * accs_per_node + start_pos + 6
                )
            )

    def set_launch_args(self):
        base = ""
        if self.conn_type == connect_type.all_to_all:
            base = "./echo_node --data-dir={datadir}/{dir} {p2p} {rpc} --genesis-json genesis.json {acc_infos}"
        else:
            base = "./echo_node --data-dir={datadir}/{dir} {p2p} {rpc} --genesis-json genesis.json {acc_infos} --config-seeds-only"
        for i in range(self.node_count):
            rpc = "--rpc-endpoint={}:{}".format(self.addresses[i], self.rpc_ports[i])
            p2p = "--p2p-endpoint={}:{} {}".format(
                self.addresses[i], self.ports[i], self.seed_node_args[i]
            )
            self.launch_strs.append(
                base.format(
                    datadir=self.echo_data_dir,
                    dir=self.node_names[i],
                    dnum=i,
                    p2p=p2p,
                    rpc=rpc,
                    acc_infos=self.account_info_args[i],
                )
            )

    def set_committee_count(self, count):
        self.committee_count = 20
        if count > self.committee_count:
            self.committee_count = count

    def form_serial_connection(self):
        self.seed_node_args.append("")
        for i in range(1, self.node_count):
            self.seed_node_args.append(
                "--seed-node={}:{}".format(self.addresses[i - 1], self.ports[i - 1])
            )

    def form_circlular_connection(self):
        self.seed_node_args.append("")
        for i in range(1, self.node_count):
            self.seed_node_args.append(
                "--seed-node={}:{}".format(self.addresses[i - 1], self.ports[i - 1])
            )
        self.seed_node_args[0] = "--seed-node={}:{}".format(
            self.addresses[self.node_count - 1], self.ports[node_count - 1]
        )

    def form_all_to_all_connection(self):
        for i in range(0, self.node_count):
            seed_args = ""
            for j in range(0, self.node_count):
                if i != j:
                    seed_args = seed_args + (
                        "--seed-node={}:{} ".format(self.addresses[j], self.ports[j])
                    )
            self.seed_node_args.append(seed_args)

    def form_all_to_all_remote_connection(self):
        self.form_all_to_all_connection()
        for i in range(self.node_count):
            seed_args = ""
            for addr, count in self.host_addresses.items():
                for j in range(count):
                    seed_args = seed_args + (
                        "--seed-node={}:{} ".format(addr, self.port + j)
                    )
            self.seed_node_args[i] = self.seed_node_args[i] + seed_args

    def copy_to(self, dst, *args):
        name, dst = dst.split(":")
        container = client.containers.get(name)
        for src in args:
            with simple_tar(src) as tar_file:
                container.put_archive(os.path.dirname(dst), tar_file)

    def copy_data(self):
        for name in self.node_names:
            print("Prepare data for", name)
            self.copy_to(
                "{}:/".format(name),
                RESOURCES_DIR + "/access.json",
                RESOURCES_DIR + "/genesis.json",
            )
            self.copy_to("{}:/echo_node".format(name), self.echo_bin)
        print("Preparing data - Done")
        print("")

    def start_nodes(self):
        f = open("cmd.log", "w+")
        container = client.containers.get(self.node_names[0])
        cmd = "/bin/sh -c '{}'".format(self.launch_strs[0])
        f.write("Started echonode0 with next cmd:\n")
        f.write(cmd + "\n\n")
        print("Starting echo_node in", self.node_names[0], "container")
        container.exec_run(cmd, detach=True)
        for i in range(1, self.node_count):
            container = client.containers.get(self.node_names[i])
            cmd = "/bin/sh -c '{}'".format(self.launch_strs[i])
            while (
                self.conn_type != connect_type.all_to_all
                and self.node_is_not_started(
                    self.addresses[i - 1], self.rpc_ports[i - 1]
                )
            ):
                time.sleep(1)
            print("Starting echo_node in", self.node_names[i], "container")
            container.exec_run(cmd, detach=True)
            f.write("Started echonode{} with next cmd:\n".format(i))
            f.write(cmd + "\n\n")
        f.close()
        print("")

    def start_containers(self):
        volumes = {self.vol_folder: {"bind": "/tmp", "mode": "rw"}}
        for i in range(self.node_count):
            container = client.containers.run(
                self.image,
                detach=True,
                name=self.node_names[i],
                remove=True,
                tty=True,
                cap_add=["SYS_PTRACE"],
                user=os.geteuid(),
                volumes=volumes,
                ports={
                    "{}/tcp".format(self.rpc_ports[i]): (
                        self.host_ip,
                        self.rpc_ports[i],
                    ),
                    "{}/tcp".format(self.ports[i]): (self.host_ip, self.ports[i]),
                },
                ulimits=[docker.types.Ulimit(name="core", soft=-1, hard=-1)],
            )
        print("")

    def stop_containers(self):
        for name in self.node_names:
            try:
                container = client.containers.get(name)
                container.stop()
                print("Stopped", name, "container")
                container.remove()
            except docker.errors.APIError:
                pass
        print("")

    def node_is_not_started(self, addr, port):  # return true if node is not started yet
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((addr, port))
        sock.close()
        return result

    def get_addresses(self):
        return self.addresses

    def get_node_names(self):
        return self.node_names

    def run_pumba(self, nodes, time, jitter):
        self.pumba_started = True
        cmd = "{pumba_bin} netem --interface=eth0 --duration 7200m --tc-image gaiadocker/iproute2 delay --time {time} --jitter {jitter} --correlation 0 {containers}"
        self.pumba_proc = subprocess.Popen(
            cmd.format(
                pumba_bin=self.pumba_bin, time=time, jitter=jitter, containers=nodes
            ),
            shell=True,
            preexec_fn=os.setsid,
        )

    def wait_nodes(self):
        for i in range(self.node_count):
            print("Waiting ws server on", self.node_names[i], "-", end=" ")
            while self.node_is_not_started(self.addresses[i], self.rpc_ports[i]):
                time.sleep(1)
            print("Done")
        # time.sleep(10) # unexplored behavior: without sleep node can crash during running
        print("Node deploying - Done")
        print("")

    def kill_pumba(self):
        if self.pumba_started == True:
            os.killpg(os.getpgid(self.pumba_proc.pid), signal.SIGKILL)

    def get_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        return host_ip

    def get_all_node_count(self):
        n = 0
        for _, node_count in self.host_addresses.items():
            n += node_count
        n += self.node_count
        return n

    def remote_deploying(self):
        if not self.host_addresses:
            if self.start_node != 0:
                raise RuntimeError(
                    "If host info is empty, then server number on which node will be deployed should be zero"
                )
        node_count = self.get_all_node_count()
        self.set_node_names()
        self.set_ports()
        self.stop_containers()  # stop before start if not stopped in previous run
        self.start_containers()
        self.set_node_addresses()
        self.form_all_to_all_remote_connection()
        self.set_remote_account_info_args()
        self.copy_data()
        self.set_launch_args()
        self.start_nodes()

    def local_deploying(self):
        self.set_node_names()
        self.set_ports()
        self.stop_containers()  # stop before start if not stopped in previous run
        self.start_containers()
        self.set_node_addresses()
        self.set_seed_node_args()
        self.set_account_info_args()
        self.copy_data()
        self.set_launch_args()
        self.start_nodes()

    def create_volume_dir(self, volume_dir, clear_volume):
        if volume_dir == "":
            dirname = os.path.dirname(__file__)
            self.vol_folder = dirname + "/../../tmp"
        else:
            self.vol_folder = volume_dir
        if not os.path.exists(self.vol_folder):
            os.makedirs(self.vol_folder)
        dirlst = os.listdir(self.vol_folder)
        if clear_volume:
            if dirlst:
                print("Clear tmp folder after previous run")
                for filename in dirlst:
                    file_path = os.path.join(self.vol_folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print("Failed to delete %s. Reason: %s" % (file_path, e))
                print("Clearing - Done")

    def create_genesis(self):
        acc_lst = []
        for i in range(self.committee_count):
            acc_lst.append(
                create_init_account(
                    self.account_names[i], self.public_keys[i], self.public_keys[i]
                )
            )
        genesis_str = get_genesis_string(acc_lst)
        dirname = os.path.dirname(__file__)
        fname = dirname + "/../resources/genesis.json"
        with open(fname, "w") as text_file:
            text_file.write(genesis_str)

    def copy_log_configs(self, clear_volume):
        if clear_volume:
            base = "/echorand_test_datadir/echonode{}"
            dirname = os.path.dirname(__file__)
            config_file = dirname + "/../resources/log_config.ini"
            for i in range(self.node_count):
                echo_folder = self.vol_folder + base.format(i)
                os.makedirs(echo_folder)
                copy(config_file, echo_folder)

    def remove_my_host(self, hosts_info):
        copy = dict(hosts_info)
        copy.pop(self.host_ip, None)
        return copy
