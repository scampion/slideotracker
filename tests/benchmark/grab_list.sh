#!/bin/bash
while read URL
do  
    sh grab.sh $URL
done < $1







