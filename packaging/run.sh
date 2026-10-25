#!/bin/sh
# Launch the game with the config file shipped next to it.
# Running from this directory keeps highscores.json beside the executable.
cd "$(dirname "$0")" && ./pac-man config.json
