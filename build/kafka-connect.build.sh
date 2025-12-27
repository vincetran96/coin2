#! /usr/bin/env bash
IMAGE_TAG=$1

docker build -t "${IMAGE_TAG}" -f ./build/kafka-connect.Dockerfile .
