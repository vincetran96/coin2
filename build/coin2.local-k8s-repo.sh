#! /usr/bin/env bash
IMAGE=docker.io/$1
OUTPUT=coin2.tar
docker save $IMAGE -o $OUTPUT
# sudo k3s crictl rmi $IMAGE
sudo ctr -n k8s.io -a /run/k3s/containerd/containerd.sock image import $OUTPUT
rm $OUTPUT
