#!/bin/bash

# This script allows Travis CI to log in Docker.

echo $2 | docker login --username $1 --password-stdin
