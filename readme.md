### How to run script:  

There are some suites in test:

* tps - measure tps, parameters which can be specified for suite: node count (`-nc` / `--node_count` - how much nodes will be deployed), transaction count (`-tc` / `--tx_count` - how much transactions will be sent during test), delay (`-t` / `--time` - in ms), list of nodes, on which delay will be started (`-dn` / `--delayed_node` - node numbers, on which interfaces pumba will run, `-idn` / `--inverse_delayed_node` - node numbers, which will run without any delay, but all other nodes will with delay), transaction type (transfer, create evm/x86-64 contracts, call evm/x86-64) (`-tt` / `--tx_type`), connection type between nodes (`-ct` / `--conn_type` - connection may be next: serial, all to all, cyclic)  
* propagation - measure time when transaction sent from one node will reach last node. In this test connection type always - serial. Parameters of this case: node count (`-nc` / `--node_count`), delay (`-t` / `--time`), list of delayed nodes (`-dn` / `-idn`)  
* database - measure blockchain database in whole, evm and x86-64 databases, also cpu utilization during test, parameters: node count (`-nc`), transaction count (`-txs`), cycles (`-sc` / `--send_cycles`) - how much times repeat transation sending => all txs = txs * cycles. This suite needed for determine, how much blockchain will occupy memory, transactions will sent in next proportion: 88% - transfers, 4% - create contract transactions, 8% - call contract transactions.  
* load - this case try to load all nodes with transactions in different threads. Transactions are divided into portions how described earlier and sent to all nodes, so here all sent transactions = node_count * txs * cycles. This suite needed for nodes stress testing. Parameters: node count, delay, connection type, transaction count, cycles.  

    Required parameters for all suites: path to echo binary (`-e` / `--echo_bin`), if delay present in parameter for suite, then it should be specified (`-p` / `--pumba_bin`), image - docker image for containers (`-t` / `--image`), image for tests with delay should be created from Dockerfile in resources folder, or you can use another image, but image should have tc command. In ubuntu this done by iproute2 package. So, if no delay specified for tps suite, you can use any image you want. For selection of suites described earlier use (`-s` / `--suite`)  

    Examples:  
    * `python3 main.py -s tps -n 2 -e ~/echo/build/bin/echo_node -p ~/pumba/.bin/pumba -t 100 -i ubuntu_delay -txs 10000 -ct all_to_all` - command will run tps suite with 2 nodes, with delay time 100ms, name of docker image - ubuntu_delay, transaction count - 10000, connection type between nodes - all to all. If no delayed nodes specified - then delay will be started on every node. if `-t` option not specified or specified with 0, then there is no delay, and special image with tc package not required.  

    * `./main.py -s propagation -n 5 -e ~/echo/build/bin/echo_node -p ~/pumba/.bin/pumba -t 50 -i ubuntu_delay -dn 0 1 2` - command will run propagation suite with 5 nodes, delay time - 50ms, nodes with delay parameter - echonode0, echonode1, echonode2. Name of containers - echonode{n}, where n - number of node started from 0.  
 
    It is convenient to leave nodes runnning after test done, for debugging purposes, but if you don't need that - use (`-cl` / `--clear`). After execution - all containers will be deleted. You should remember, that deploying containers is not very fast, especially if you don't clear it after previous execution, so you should wait some time. Docker containers have shared folder with host and it is mapped at `bm-scripts/tmp` folder. You can find there logs of nodes. Also you can find cmd.log at `bm-scripts` folder, there will be placed commands with which nodes started.  

    Result of utilization checker will be places at results folder and number of pid: results/{pid}. Pid will be printed at the end of test execution. Following columns are present in result file: block number, rss - resident memory size, in top RES column, vms - virtual memory size, in top VIRT column, cpu utilizarion in %, whole blockchain size, x86-64 database size, emv database size. All measures in bytes.

### Deploying on few servers:

There are some files for deploying nodes on different servers and measure some node indicators (tps, utilization):

* start_deployer.py - allow node deploying on servers, have such required arguments like:(`-n` / `--node_count`) - specify number of nodes will be deployed on current server, (`-e` / `--echo_bin`) - specify path to echo_node binary, (`-i` / `--image`) - specify image for docker containers, (`-sn` / `--server_num`) - specify serial number of server to start, started from 0, (`-hi` / `--hosts_info`) - specify information about other hosts, should be in json format (`-hi '{"ip_address":number_of_nodes, "ip_address":number_of_nodes, ...}'`), (`-cc` / `--committee_count`) - specify number of initial accounts in genesis.json file. This file will be generated at `scripts/resources` folderi, (`-u` / `--url`) -specify url string of slack app, where node alerts should be send.
* start_sender.py - needed for sending transactions on nodes. Required argumets: (`-hi` / `--hosts_info`) - specify information about hosts, the same like in start_deployer.py, (`-txs` / `--txs_count`) - specify number of transaction which will be sent on all host, specified in `-hi`, transaction. Transactions are sent sequentially on all nodes, (`-d` / `--delay`) - delay between transfers in seconds, (`-n` / `--accout_num`) - specify number of accounts on all nodes, this argument required.
* start_tpschecker.py - needed for starting tps checker. Required arguments: (`-txs` / `--txs_count`) - specify how much transactions should be sent to nodes until check will be stopped, (`-a` / `--addres`) - specify ip address for connection, (`-p` / `--port`) - specify port for connection.
* start_uchecker - start utilization checker for measuring blockchain database in whole, evm and x86-64 databases, also cpu utilization. Required arguments: (`-n` / `--node_count`) - number of nodes will be registering in utilization checker. This checker should be started on server you are interested in, it scanning processes and try to find echo_node process. (`-t` / `--time`) - time in seconds during which utilization checker will work.

    Example (starting 100 nodes on 4 servers, 25 nodes per server):
    * `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 0 -hi '{"192.168.9.41":25, "192.168.9.42":25, "192.168.9.43":25}' -cc 100 -u "url_of_slack_app"`  
      `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 1 -hi '{"192.168.9.40":25, "192.168.9.42":25, "192.168.9.43":25}' -cc 100 -u "url_of_slack_app"`  
      `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 2 -hi '{"192.168.9.40":25, "192.168.9.41":25, "192.168.9.43":25}' -cc 100 -u "url_of_slack_app"`  
      `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 3 -hi '{"192.168.9.40":25, "192.168.9.41":25, "192.168.9.42":25}' -cc 100 -u "url_of_slack_app"`  

    Example (starting sender, which will send 200 tx for every 2 seconds):
    * `./start_sender.py -hi '{"192.168.9.40":25, "192.168.9.41":25, "192.168.9.42":25, "192.168.9.43":25}' -txs 200 -n 100 &> send.log &` - it is more convenient to start it in daemon mode. (`-cc`) argument in start_deployer.py and (`-n`) in start_sender.py should be equal. After start_deployer.py started alerts.log file will be generated. Here you can see current tps.

### Core dumps

For generating core dumps, you should write core pattern by next command on your host: `echo '/tmp/core.%t.%e.%p.%P' | sudo tee /proc/sys/kernel/core_pattern`

### Debugging

For getting just backtrace you can use one of next methods:

Method 1:

* Use `docker exec -it echonode{n} /bin/bash` to get access to container and run `gdb -p $PID command`.  

Method 2:

* You can get access to process inside container from your host using nsenter: `sudo nsenter -t $HPID -m -p gdb -p $PID`, where `$HPID` - it is host pid and `$PID` - it is pid inside container.  

This methods give you backtrace, also there is available to put breakpoints, but no source code available. For fully debuggin use next method:

* run `gdb /path/to/echonode` and inside gdb run next command `(gdb) target remote | docker exec -i echonode{n} gdbserver - --attach $PID`, this give you opportunity to debug process inside container with source code.
