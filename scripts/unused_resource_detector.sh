#!/bin/bash

#
# Run this script to see if a ressource is used in the code
#

for line in $(find resources  -type f -not -path  '*/\.*' -exec basename {} \; )
do
    grep -R "$line" gns3 > /dev/null
    if [ $? -eq 1 ]
    then
        echo "Unused ressource $line"
    fi
done
