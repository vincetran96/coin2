This file contains the steps required to setup K3s on the machine. Assume that Tailscale is already installed.

Create a file named `/etc/ufw/applications.d/k3s` with the following content:
```conf
[K3s]
title=K3s ports
description=Required by K3s: https://docs.k3s.io/installation/requirements#networking
ports=2379:2380/tcp|6443/tcp|8472/udp|10250/tcp|51820/udp|51821/udp|5001/tcp
```

Run the following command:
```bash
export TAILSCALE_IP=XX.XX.XX.XX
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --disable traefik --disable servicelb --write-kubeconfig $HOME/.kube/config --write-kubeconfig-mode 644 --flannel-iface tailscale0 --node-ip $TAILSCALE_IP --node-external-ip $TAILSCALE_IP" K3S_TOKEN=12345 sh -
```
