### Help for start_sender.py

This script needed for sending transactions of differrent types with next options:
* `-hi`  - hosts info flag, the same as in start_deployer, for more information see start_deployer.md
* `-txs` - number of transaction will be send
* `-d`   - delay between transactions in seconds
* `-tt`  - transaction type, see `--help` for information about arguments
* `-sn`  - sender_number (or sequence_number) - the same as in start_deployer, see start_deployer.md
* `-s/--start_new` - if this flag not specified - then previous start_sender process will be killed
* `-t/--tps`   - if this argmunets specified, then sender will hold tps equal to amount of txs argmunets, if not specified - then highier, or less, if signing of then bunch of transactions take more then 1 second
* `-mp`   - sender will run in parallel mode, with specified number of daughter processes.

### Example

This command will run second instance of start_sender.py (-sn 1) without killing first start_sender (-s), transaction will be send to all nodes one by one without any delay  
`./start_sender.py -hi '{"192.168.9.40":4, "192.168.9.41":3, "192.168.9.42":3, "192.168.9.43":4}' -txs 100 -d 0 -s -sn 1`

### Help for import_balance.py, distribute_balance.py

This script needed for importing nathan balance and distribution between accounts. Scripts have next options:
* `-a` - ip address of rpc endpoint of the node
* `-p` - port of rpc endpoint of the node

### Example

`./import_balance.py -p 8090 -a 172.17.0.2` - here specified docker ip address, where node deployed
`./distribute_balance.py -p 8090 -a 172.17.0.2`
