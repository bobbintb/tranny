#!/bin/bash

WATCH_DIR=$1
SCRIPT_PATH=./scripts/tranny-add.py

echo "Watching directory for torrents: $WATCH_DIR"

if [ ! -d $WATCH_DIR ]; then
    echo "Directory does not exist"
    exit 1
fi
while true; do
$SCRIPT_PATH $WATCH_DIR/* && echo "cleaning up" && rm -rf $WATCH_DIR/*.torrent;
sleep 1;
done
