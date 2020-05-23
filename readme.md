### Project setup:

1. Install docker  
2. Install proect dependencies by running `bash install.sh`.  
3. Fix docker permissions with next commands:  
`sudo groupadd docker`  
`sudo usermod -aG docker $USER`  
`newgrp docker`  

4. Build ubuntu_delay image with: `docker build -t ubuntu_delay ./scripts/resources`
5. See "Core dumps" section
6. See "Debugging" section
7. See "Examples" section
8. See docs folder for more start examples

### Core dumps

Here can be situations, when something went wrong and you should have informations about this situations, core dumps will help you.
For generating core dumps, you should write core pattern by next command on your host: `echo '/tmp/core.%t.%e.%p.%P' | sudo tee /proc/sys/kernel/core_pattern`.
For permanent storing core_pattern (it will be changed for next computer start), you should write rule `kernel.core_pattern=/tmp/cores/core.%t.%e.%p.%P` to file `/etc/sysctl.conf`.

### Debugging

For getting just backtrace you can use one of next methods:

* Use `docker exec -it echonode{n} /bin/bash` to get access to container and run `gdb -p $PID command`.  
* You can get access to process inside container from your host using nsenter: `sudo nsenter -t $HPID -m -p gdb -p $PID`, where `$HPID` - it is host pid and `$PID` - it is pid inside container.  
This methods give you backtrace, also there is available to put breakpoints, but no source code available. For fully debuggin use next method:

* run `gdb /path/to/echonode` and inside gdb run next command `(gdb) target remote | docker exec -i echonode{n} gdbserver - --attach $PID`, this give you opportunity to debug process inside container with source code.

### Examples (starting nodes on servers):

Starting 25 nodes per server:
* `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 0 -hi '{"192.168.9.41":25, "192.168.9.42":25, "192.168.9.43":25}' -cc 100 -u "url_of_slack_app"`
  `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 1 -hi '{"192.168.9.40":25, "192.168.9.42":25, "192.168.9.43":25}' -cc 100 -u "url_of_slack_app"`
  `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 2 -hi '{"192.168.9.40":25, "192.168.9.41":25, "192.168.9.43":25}' -cc 100 -u "url_of_slack_app"`
  `./start_deployer.py -n 25 -e ./echo_node -i ubuntu_delay -sn 3 -hi '{"192.168.9.40":25, "192.168.9.41":25, "192.168.9.42":25}' -cc 100 -u "url_of_slack_app"`

Starting sender:
* `./start_sender.py -hi '{"192.168.9.40":25, "192.168.9.41":25, "192.168.9.42":25, "192.168.9.43":25}' -txs 200`

More information about options you can get with `--help` command, it available on all scripts, or see docs folder.
