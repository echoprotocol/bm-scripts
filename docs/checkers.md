### Help for alerts.py

This script needed for checking nodes existing, checking tps and if something will wrong, then alert will be send to slack app, start_deployer try to start this script automatically, but you can run it by hand. Script have next options:
*  `-u` - url where alert should be sent
*  `-n` - number of nodes on server (for their controlling)
*  `-sn` - specify server name for identifiying where error happens
*  `-a`  - address where tps checker will be connected
*  `-p` - rpc port for tps chekcer connecting
*  `-ti` - interval between tps measures, higher interval - more precisious results
*  `-t/--with_tps` - if flag specified, then message about low tps will be send, this is done for decreasing spam messages from many servers, because you can measure tps only on one host, and it will be the same on all others hosts

### Example

Starting alerts script for controlling four nodes, server name - "echo1", interval between tps measures 300 seconds.
`./alerts.py -u https://hooks.slack.com/services/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 -n 4 -sn echo1 -ti 300`

### Help for start_tpschecker.py

This script needed for one time tps cheking by specifying amount of expected transactions. After this script will be closed. Script options:
* `-txs` - number of expected transactions, when tps_checker collect them - it will be closed with results.
* `-a`   - address where checker will be connected
* `-p`   - rpc port endpoint port

### Example

Connecting to first docker container and wait while tps_checker collect 10000 transactions.
`./start_tpschecker -txs 10000 -a 172.17.0.2 -p 8090`

### Help for start_uchecker

This script needed for checking such utilization parameters as: cpu, memory, blockchain size. Script options:
* `-n` - number of nodes which will be tracked
* `-v` - path to shared folder between host and docker

### Example

Tracking 4 nodes:
`./start_uchecker.py -n 4 -v "/mnt/data/tmp"`
