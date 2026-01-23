#!/usr/bin/bash

ps -ef | awk -v me=$$ '$6 ~ /^pts/ && $2 != me && $2 != 1 {print $2}' | xargs -r kill -9
