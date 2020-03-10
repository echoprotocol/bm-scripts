### How to run script:  

There are some suites in test:

* tps - measure tps, parameters which can be specified for suite: node count (`-nc` / `--node_count`), transaction count (`-tc` / `--tx_count`), delay (`-t` / `--time`), list of nodes, on which delay will be started (`-dn` / `--delayed_node`, `-idn` / `--inverse_delayed_node`), transaction type (transfer, create evm/x86-64 contracts, call evm/x86-64) (`-tt` / `--tx_type`), connection type between nodes (`-ct` / `--conn_type`)  
* propagation - measure time when transaction sent from one node will reach last node. In this test connection type always - serial. Parameters of this case: node count, delay, list of delayed nodes  
* database - measure blockchain database in whole, evm and x86-64 databases, also cpu utilization during test, parameters: node count, transaction count, cycles (`-sc` / `--send_cycles`) - how much times repeat transation sending (for all tx types)  
* load - this case try to load all nodes with transactions in different threads. Transactions are divided into equal portions and sent to all nodes. Parameters: node count, delay, connection type, transaction count, cycles.  

    Required parameters for all suites: path to echo binary (`-eb` / `--echo_bin`), if delay present in parameter for suite, then it should be specified (`-pb` / `--pumba_bin`), image - docker image for containers (`-t` / `--image`), if delay present in parameter for suite, then image should be created from Dockerfile in resources folder, or you can use another image, but image should have tc command. In ubuntu this done by iproute2 package. So, if no delay specified for tps suite, you can use any image you want. For selection suite use (`-s` / `--suite`)  

    Examples:  
    * `python3 main.py -s tps -n 2 -e ~/echo/build/bin/echo_node -p ~/pumba/.bin/pumba -t 100 -i ubuntu_delay -txs 10000 -ct all_to_all` - command will run tps suite with 2 nodes, with delay time 100ms, name of docker image - ubuntu_delay, transaction count - 10000, connection type between nodes - all to all. If no delayed nodes specified - then delay will be started on every node. if `-t` option not specified or specified with 0, then there is no delay, and special image with tc package not required.  

    * `./main.py -s propagation -n 5 -e ~/echo/build/bin/echo_node -p ~/pumba/.bin/pumba -t 50 -i ubuntu_delay -dn 0 1 2` - command will run propagation suite with 5 nodes, delay time - 50ms, nodes with delay parameter - echonode0, echonode1, echonode2. Name of containers - echonode{n}, where n - number of node started from 0.  
 
    It is convenient to leave nodes runnning after test done, for debugging purposes, but if you don't need that - use (`-cl` / `--clear`). After execution - all containers will be deleted. You should remember, that deploying containers is not very fast, especially if you don't clear it after previous execution, so you should wait some time.  

    Result of utilization checker will be places at results folder and number of pid: results/{pid}. Pid will be printed at the end of test execution. Following columns are present in result file: block number, rss - resident memory size, in top RES column, vms - virtual memory size, in top VIRT column, cpu utilizarion in %, whole blockchain size, x86-64 database size, emv database size. All measures in bytes.
