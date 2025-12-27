This file contains the steps required to setup Kafka on the machine.

Run the following:
Copy everything in the the `build` directory to this target directory on the VM host: `$HOME/coin2`.

Create a file named `/etc/ufw/applications.d/kafka` with the following content:
```conf
[Kafka]
title=Kafka ports
description=For access into Kafka Docker cluster
ports=9200:9204/tcp
```

Run the following command:
```bash
sudo ufw allow Kafka
```
