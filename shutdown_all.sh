#!/bin/bash

for node in {94..99}; do
    echo "Bringing down Future-Crew on 192.168.1.$node"
    ssh -i ~/pi-key pi@192.168.1.$node "sudo shutdown -h now"
done
