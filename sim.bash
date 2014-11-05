#!/bin/sh

TRACES=traces/*.trace

for f in $TRACES
do
    echo "Starting $f"
    python phone.py $f &
done
