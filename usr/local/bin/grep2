#!/bin/bash

for i in $* ;do
    LIST=`ls $i`
    for j in $LIST; do
        echo $i/$j
        grep '0.34403 -0.10976 -0.81854 -1.03689 -0.30831 -0.69549 -0.11242 -0.31376 -0.62408 -0.46552 -0.31111 -0.51388' $i/$j
    done
done

