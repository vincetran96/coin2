#! /usr/bin/env bash
IMAGE_TAG=vincetran96/coin2:test

docker build --no-cache -t "${IMAGE_TAG}" -f ./build/coin2.Dockerfile .
