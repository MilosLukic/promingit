#!/bin/bash
# Log extraction script, extracts log and runs program to collect data from log.

cd ..
git log --pretty=format:"start%n%h;%ae;%at;%cE;%ct;%d;%nstartcomment%n%s;%nend" --numstat > promingit/logs/project_gitlog.log
cd promingit
python main.py