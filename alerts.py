#!/usr/bin/python3

import argparse
import requests
import json
import time
import psutil
import signal
from datetime import datetime
from scripts.node_deployer.tps_checker import tps_checker
from sys import maxsize
import logging

def send_alert(msg, url):
    print("Sending alert with msg:", msg, flush=True)
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8'}

    now = datetime.now()
    time = now.strftime("%H:%M:%S")

    data = {"username":"here", "text":"<!here> {}  {}".format(msg, time)}
    answer = requests.post(url, data=json.dumps(data), headers=headers)
    print(answer.text)

def create_missed_msg(server_name, missed):
    msg="[ALERT]: Can not find node(s) on server {}: {}"
    nodes=""
    for i in missed:
        nodes=nodes+"echonode{} ".format(i)
    return msg.format(server_name, nodes)

def check_nodes(num_nodes):
    missed_list=set()
    base="--data-dir=./tmp/echorand_test_datadir/echonode{}"
    for i in range(num_nodes):
        missed=True
        for proc in psutil.process_iter():
            if (proc.name() == "echo_node" and base.format(i) in proc.cmdline()):
                missed=False
        if (missed == True):
            missed_list.add(i)
    print("Nodes checking - Done", flush=True)
    return missed_list

def set_options(parser):
    parser.add_argument('-u', '--url', action='store', dest='url',
        type=str, help="Url where alert should be sent", required=True)
    parser.add_argument('-sn', '--server_name', action='store', dest='server_name',
        type=str, help="Name of server", default="", required=True)
    parser.add_argument('-n', '--num_nodes', action='store', dest='num_nodes',
        type=int, help="Number of nodes which started on host", default="", required=True)
    parser.add_argument('-a', '--address', dest='address', action='store',
        type=str, help="Address for connecting", default="172.17.0.2")
    parser.add_argument('-p', '--port', dest='port', action='store',
        type=int, help="Rpc port for connecting", default=8090)
    parser.add_argument('-ti', '--time_interval', action='store', dest='time_interval',
        type=int, help="Time interval between tps measures (in seconds)", default=300)
    parser.add_argument('-t', '--with_tps', action='store_true', help="Enable tps alerts")

def main():
    t=None
    def signal_handler(sig, frame):
        print("\nCaught SIGINT:")
        if t is not None:
            t.interrupt_checker()
        raise SystemExit("Exited from Ctrl-C handler")
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Help for bm-scripts binary")
    set_options(parser)
    args = parser.parse_args()

    missed=set()
    t=tps_checker(args.address, args.port, maxsize)
    connected_to=args.port - 8090
    print("Connected to", args.address, args.port)
    t.run_check()

    resolved_low_tps = True

    while True:
        tmp=check_nodes(args.num_nodes)
        diff=tmp-missed
        if (diff):
            send_alert(create_missed_msg(args.server_name, diff), args.url)
            missed=tmp

        if (connected_to in missed):
            send_alert("[ALERT]: Node where tps checker was connected can not be found, stopping alert system!", args.url)
            break

        t.collected_tx_number=0
        time.sleep(args.time_interval)
        tps=t.collected_tx_number/args.time_interval
        print(datetime.now().strftime("%H:%M:%S"), "current tps:", tps, "block num:", t.block_number, flush=True)
        
        if (tps < 10):
            if args.with_tps == True and resolved_low_tps == True:
                send_alert("[ALERT]: Low tps {} on server {}".format(tps, args.server_name), args.url)
                resolved_low_tps = False
        else:
            if resolved_low_tps == False:
                resolved_low_tps = True
                send_alert("[OK]: Resolved low tps {} on server {}".format(tps, args.server_name), args.url)

        if (len(missed) == args.num_nodes):
            break

    t.interrupt_checker()

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        print(e)
    except Exception as e:
        logging.error(traceback.format_exc())
