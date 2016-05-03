#!/bin/sh
. /etc/profile
if ! tmux attach -t menu 2>/dev/null
then
tmux new -d -s menu ./menu.py
tmux set-option -t menu status off
tmux attach -t menu
fi
