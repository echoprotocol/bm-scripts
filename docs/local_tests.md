### Help for main.py

This script needed for fast local nodes testing. There are some available suites:

* tps - measure tps, parameters which can be specified for suite: node count (`-nc` / `--node_count` - how much nodes will be deployed), transaction count (`-tc` / `--tx_count` - how much transa
ctions will be sent during test), delay (`-t` / `--time` - in ms), list of nodes, on which delay will be started (`-dn` / `--delayed_node` - node numbers, on which interfaces pumba will run, `-i
dn` / `--inverse_delayed_node` - node numbers, which will run without any delay, but all other nodes will with delay), transaction type (transfer, create evm/x86-64 contracts, call evm/x86-64) (
`-tt` / `--tx_type`), connection type between nodes (`-ct` / `--conn_type` - connection may be next: serial, all to all, cyclic)
* propagation - measure time when transaction sent from one node will reach last node. In this test connection type always - serial. Parameters of this case: node count (`-nc` / `--node_count`),
 delay (`-t` / `--time`), list of delayed nodes (`-dn` / `-idn`)
* database - measure blockchain database in whole, evm and x86-64 databases, also cpu utilization during test, parameters: node count (`-nc`), transaction count (`-txs`), cycles (`-sc` / `--send
_cycles`) - how much times repeat transation sending => all txs = txs * cycles. This suite needed for determine, how much blockchain will occupy memory, transactions will sent in next proportion
: 88% - transfers, 4% - create contract transactions, 8% - call contract transactions.
* load - this case try to load all nodes with transactions in different threads. Transactions are divided into portions how described earlier and sent to all nodes, so here all sent transactions
 = node_count * txs * cycles. This suite needed for nodes stress testing. Parameters: node count, delay, connection type, transaction count, cycles.

    Required parameters for all suites: path to echo binary (`-e` / `--echo_bin`), if delay present in parameter for suite, then it should be specified (`-p` / `--pumba_bin`), image - docker ima
ge for containers (`-t` / `--image`), image for tests with delay should be created from Dockerfile in resources folder, or you can use another image, but image should have tc command. In ubuntu
this done by iproute2 package. So, if no delay specified for tps suite, you can use any image you want. For selection of suites described earlier use (`-s` / `--suite`)

### Examples

* `python3 main.py -s tps -n 2 -e ~/echo/build/bin/echo_node -p ~/pumba/.bin/pumba -t 100 -i ubuntu_delay -txs 10000 -ct all_to_all` - command will run tps suite with 2 nodes, with delay time 100ms, name of docker image - ubuntu_delay, transaction count - 10000, connection type between nodes - all to all. If no delayed nodes specified - then delay will be started on every node. if
`-t` option not specified or specified with 0, then there is no delay, and special image with tc package not required.

* `./main.py -s propagation -n 5 -e ~/echo/build/bin/echo_node -p ~/pumba/.bin/pumba -t 50 -i ubuntu_delay -dn 0 1 2` - command will run propagation suite with 5 nodes, delay time - 50ms, nodes with delay parameter - echonode0, echonode1, echonode2. Name of containers - echonode{n}, where n - number of node started from 0
