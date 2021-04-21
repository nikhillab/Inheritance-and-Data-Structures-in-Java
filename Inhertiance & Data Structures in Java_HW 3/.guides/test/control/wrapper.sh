#!/bin/bash

timeout 175 /home/codio/workspace/.guides/secure/control/execute.py > /tmp/output_temp.txt
RC=$?
echo "Exit code $RC"
tail /tmp/output_temp.txt -n 5000
if [ $RC == 9 ] || [ $RC == 124 ]; then
    if [ $RC == 124 ]; then
        echo "Execution timeout."
    fi
    python3 /home/codio/workspace/.guides/secure/control/execute.py force
fi