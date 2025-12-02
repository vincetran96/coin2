#! /usr/bin/env bash
IMAGE_TAG=$1

docker build --no-cache -t "${IMAGE_TAG}" -f ./build/coin2.Dockerfile .
