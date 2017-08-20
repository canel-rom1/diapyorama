#!/bin/bash


git remote update

local=`git rev-list --max-count=1 latest`
distant=`git rev-list --max-count=1 origin/latest`

if [ "$local" != "$distant" ]
then
	kill `ps -eF | grep diapyorama.py | head -n1 | awk '{ print $2 }'`
	git pull --rebase origin latest
	python3 /home/diapy/bin/diapyorama.py
fi

