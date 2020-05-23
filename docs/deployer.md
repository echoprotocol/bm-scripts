### Help for start_deployer.py

This script allow node deploying on servers, have such required arguments like:
* `-n`   - number of nodes will be deployed on current server 
* `-e`   - path to echo_node binary
* `-i`   - name of image for docker (from readme.md it is ubuntu_delay), 
* `-sn`  - sequence number of start_deployer process, this value started from 0, next start_deployer running should be started with next sequence number
* `-hi`  - specify information about other hosts, should be in json format (hosts info should be the same on all servers) Format: - '{"ip_addr":amount_of_nodes}'
* `-cc`  - number of initial accounts on chain
* `-u`   - url of slack app where alerts will be send(such as low tps, or nodes crashing will be send), format next: "https://url_of_slack_service"
* `-v`   - path to shared folder between host and docker
* `-d`   - time in ms for delay on network interfaces, if 0 - then no delay
* `-p`   - path to pumba binary (this is tool whick makes available network delay)
* `-t`   - this flag should be specified without any arguments, if specified - then low tps alerts will be send to slack app, else only nodes crashing information
* `-ti`  - time interval between tps measures, (start_deployer run alerts.py and this flag needed for changing default time value 300 in alerts.py)
* `-uc`  - (no required arguments for this flag) needed for automatic starting utilization_checker
* `-clv` - clear shared folder content after previous start_deplyoer run

### Example

Description: deploying 4 nodes on first server with 16 initial accounts (from hosts info `-hi` - you can see: our ip "192.168.9.41").
`./start_deployer.py -n 4 -e ./echo_node -i ubuntu_delay -sn 0 -hi '{"192.168.9.41":4, "192.168.9.42":2, "192.168.9.43":2, "192.168.9.44":8}' -cc 16 -u "https://hooks.slack.com/services_id" -v "/mnt/data/tmp" -d 0 -p "./pumba" -clv -t`
