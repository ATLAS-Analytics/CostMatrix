#!/bin/bash

echo -n "time> begin "; date 

python cost_matrix_probe.py > info.txt; 
cat info.txt

echo -n "time> finished all the tests "; date
