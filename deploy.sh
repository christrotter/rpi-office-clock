#!/bin/bash

$ERRORSTRING="Error. Please make sure you've indicated correct parameters"
if [ $# -eq 0 ]
    then
        echo $ERRORSTRING;
elif [ $1 == "live" ]
    then
        if [[ -z $2 ]]
            then
                echo "Running dry-run"
                rsync --dry-run -az --force --delete --progress --exclude-from=.gitignore -e "ssh -p22" ./ pi@192.168.86.114:/home/pi/rpi-office-clock
        elif [ $2 == "go" ]
            then
                echo "Running actual deploy"
                rsync -az --force --delete --progress --exclude-from=.gitignore -e "ssh -p22" ./ pi@192.168.86.114:/home/pi/rpi-office-clock
        else
            echo $ERRORSTRING;
        fi
fi
