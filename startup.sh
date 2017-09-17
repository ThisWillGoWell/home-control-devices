#!/bin/bash
SESSION="DINOLIGHT"
tmux -2 new-session -d -s $SESSION

#setup webapp and server
tmux new-window -t $SESSION:1 -n 'dinoapp'
tmux split-window -h
tmux select-pane -t 0
tmux send-keys "DINO_WEB_APP" C-m

tmux select-pane -t 1
tmux send-keys "DINO_SERVER" C-m
