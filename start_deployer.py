#!/usr/bin/python3

import argparse
from scripts.node_deployer.deployer import deployer
from scripts.node_sender.sender import Sender
import json
import signal
import traceback
import logging
import os
import getpass
import psutil

def kill_alert():
    my_pid = os.getpid()
    for proc in psutil.process_iter():
        if (proc.name() == "python3" and "./alerts.py" in proc.cmdline()):
            print("Killing previous alert process\n")
            os.kill(proc.pid, signal.SIGTERM)

def set_options(parser):
    parser.add_argument('-e', '--echo_bin', action='store', dest='echo_bin',
        type=str, help="Path to echo_node binary, should be statically compiled!", required=True)
    parser.add_argument('-i', '--image', action='store', dest='image',
        type=str, help="Name of image for docker containers", default="", required=True)
    parser.add_argument('-n', '--node_count', action='store', dest='node_count',
        type=int, help="Node count for deploying", default=2)
    parser.add_argument('-cc', '--committee_count', action='store', dest='committee_count',
        type=int, help="Committee count", default=20)
    parser.add_argument('-sn', '--server_num', dest='server_num', action='store',
        type=int, help="Number of server on which deployer will be started", required=True)
    parser.add_argument('-hi', '--hosts_info', dest='hosts_info', action='store',
        type=str, help="Host info in dictionary formar: {\"ip address\" : number of nodes}", default="", required=True)
    parser.add_argument('-u', '--url', dest='url', action='store',
        type=str, help="Url for alert script", default="")
    parser.add_argument('-cl', '--clear', action='store_true', help="Clear containers after test execution")

def main():
    kill_alert()

    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        raise SystemExit("Exited from Ctrl-C handler")
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    set_options(parser)
    args = parser.parse_args()
    hosts_info=json.loads(args.hosts_info)
    d = deployer(node_count=args.node_count, echo_bin=args.echo_bin, pumba_bin="",
                image=args.image, start_node=args.server_num, host_addresses=hosts_info, remote=True, committee_count=args.committee_count)
    d.wait_nodes()
    if args.server_num == 0:
        s=Sender(d.addresses[0], d.rpc_ports[0], d.committee_count)
        s.import_balance_to_nathan()
        s.balance_distribution()

    if args.url != "":
        alert_cmd='nohup python3 ./alerts.py -u \"{url}\" -n {num_nodes} -sn {sname} >alerts.log 2>&1 &'
        os.system(alert_cmd.format(url=args.url, num_nodes=args.node_count, sname=getpass.getuser()))

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        logging.error(traceback.format_exc())
