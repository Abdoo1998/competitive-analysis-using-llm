#!/bin/bash
if [ -f pids.txt ]; then
    while read pid; do
        if ps -p $pid > /dev/null; then
            echo "Stopping process $pid"
            kill $pid
        fi
    done < pids.txt
    rm pids.txt
    echo "All processes stopped"
else
    echo "No pids.txt file found. Processes may not be running."
fi
